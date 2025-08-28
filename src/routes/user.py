from flask import Blueprint, request, g
from src.models.user import db, User
from src.utils.auth import auth_required, optional_auth
from src.utils.helpers import success_response, error_response, validate_required_fields

user_bp = Blueprint('users', __name__)

@user_bp.route('/users/<user_id>', methods=['GET'])
@optional_auth
def get_user(user_id):
    """
    Obtém informações de um usuário específico
    """
    user = User.query.get(user_id)
    
    if not user:
        return error_response(
            'Usuário não encontrado',
            'RESOURCE_NOT_FOUND',
            status_code=404
        )
    
    return success_response({'user': user.to_dict()})

@user_bp.route('/users/<user_id>', methods=['PUT'])
@auth_required
def update_user(user_id):
    """
    Atualiza o perfil de um usuário
    """
    # Verificar se o usuário está tentando atualizar seu próprio perfil
    if g.current_user_id != user_id:
        return error_response(
            'Você só pode atualizar seu próprio perfil',
            'AUTHORIZATION_ERROR',
            status_code=403
        )
    
    user = User.query.get(user_id)
    
    if not user:
        return error_response(
            'Usuário não encontrado',
            'RESOURCE_NOT_FOUND',
            status_code=404
        )
    
    data = request.get_json()
    
    if not data:
        return error_response(
            'Dados JSON inválidos',
            'VALIDATION_ERROR',
            status_code=400
        )
    
    # Campos que podem ser atualizados
    updatable_fields = ['name', 'bio', 'location', 'website']
    
    for field in updatable_fields:
        if field in data:
            setattr(user, field, data[field])
    
    try:
        db.session.commit()
        return success_response({'user': user.to_dict()})
    except Exception as e:
        db.session.rollback()
        return error_response(
            'Erro ao atualizar usuário',
            'INTERNAL_ERROR',
            status_code=500
        )

@user_bp.route('/users', methods=['POST'])
def create_user():
    """
    Cria um novo usuário
    """
    data = request.get_json()
    
    if not data:
        return error_response(
            'Dados JSON inválidos',
            'VALIDATION_ERROR',
            status_code=400
        )
    
    # Validar campos obrigatórios
    required_fields = ['firebase_uid', 'name', 'email']
    missing_fields = validate_required_fields(data, required_fields)
    
    if missing_fields:
        return error_response(
            f'Campos obrigatórios ausentes: {", ".join(missing_fields)}',
            'VALIDATION_ERROR',
            {'missing_fields': missing_fields},
            status_code=400
        )
    
    # Verificar se o usuário já existe
    existing_user = User.query.get(data['firebase_uid'])
    if existing_user:
        return error_response(
            'Usuário já existe',
            'VALIDATION_ERROR',
            status_code=409
        )
    
    # Verificar se o email já está em uso
    existing_email = User.query.filter_by(email=data['email']).first()
    if existing_email:
        return error_response(
            'Email já está em uso',
            'VALIDATION_ERROR',
            {'field': 'email', 'message': 'Email já está em uso'},
            status_code=409
        )
    
    # Criar novo usuário
    user = User(
        id=data['firebase_uid'],
        name=data['name'],
        email=data['email'],
        avatar_url=data.get('avatar_url')
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        return success_response({'user': user.to_dict()}, status_code=201)
    except Exception as e:
        db.session.rollback()
        return error_response(
            'Erro ao criar usuário',
            'INTERNAL_ERROR',
            status_code=500
        )

@user_bp.route('/users/<user_id>/follow', methods=['POST'])
@auth_required
def follow_user(user_id):
    """
    Segue/deixa de seguir um usuário (toggle)
    """
    if g.current_user_id == user_id:
        return error_response(
            'Você não pode seguir a si mesmo',
            'VALIDATION_ERROR',
            status_code=400
        )
    
    current_user = User.query.get(g.current_user_id)
    target_user = User.query.get(user_id)
    
    if not current_user:
        return error_response(
            'Usuário atual não encontrado',
            'RESOURCE_NOT_FOUND',
            status_code=404
        )
    
    if not target_user:
        return error_response(
            'Usuário a ser seguido não encontrado',
            'RESOURCE_NOT_FOUND',
            status_code=404
        )
    
    # Verificar se já está seguindo
    is_following = target_user in current_user.following
    
    try:
        if is_following:
            # Deixar de seguir
            current_user.following.remove(target_user)
            action = 'removed'
        else:
            # Seguir
            current_user.following.append(target_user)
            action = 'added'
        
        db.session.commit()
        
        return success_response({
            'action': action,
            'followers_count': len(target_user.followers)
        })
    except Exception as e:
        db.session.rollback()
        return error_response(
            'Erro ao processar seguimento',
            'INTERNAL_ERROR',
            status_code=500
        )
