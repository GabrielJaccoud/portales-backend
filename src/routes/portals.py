from flask import Blueprint, request, g
from src.models.user import db, User
from src.models.portal import Portal
from src.models.category import Category
from src.models.tag import Tag
from src.models.review import Review
from src.utils.auth import auth_required, optional_auth
from src.utils.helpers import success_response, error_response, validate_required_fields, paginate_query, create_slug

portals_bp = Blueprint('portals', __name__)

@portals_bp.route('/portals', methods=['GET'])
@optional_auth
def get_portals():
    """
    Lista portais com filtros e paginação
    """
    # Parâmetros de query
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category_id', type=int)
    creator_id = request.args.get('creator_id')
    featured = request.args.get('featured', type=bool)
    search = request.args.get('search')
    
    # Query base
    query = Portal.query.filter_by(is_public=True, is_active=True)
    
    # Aplicar filtros
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if creator_id:
        query = query.filter_by(creator_id=creator_id)
    
    if featured is not None:
        query = query.filter_by(is_featured=featured)
    
    if search:
        query = query.filter(Portal.title.contains(search))
    
    # Ordenação
    query = query.order_by(Portal.created_at.desc())
    
    # Paginação
    result = paginate_query(query, page, per_page)
    
    return success_response({
        'portals': [portal.to_dict() for portal in result['items']],
        'pagination': result['pagination']
    })

@portals_bp.route('/portals/<int:portal_id>', methods=['GET'])
@optional_auth
def get_portal(portal_id):
    """
    Obtém detalhes de um portal específico
    """
    portal = Portal.query.get(portal_id)
    
    if not portal:
        return error_response(
            'Portal não encontrado',
            'RESOURCE_NOT_FOUND',
            status_code=404
        )
    
    # Verificar se o portal é público ou se o usuário é o criador
    if not portal.is_public and (not g.current_user_id or g.current_user_id != portal.creator_id):
        return error_response(
            'Portal não encontrado',
            'RESOURCE_NOT_FOUND',
            status_code=404
        )
    
    return success_response({'portal': portal.to_dict()})

@portals_bp.route('/portals', methods=['POST'])
@auth_required
def create_portal():
    """
    Cria um novo portal
    """
    data = request.get_json()
    
    if not data:
        return error_response(
            'Dados JSON inválidos',
            'VALIDATION_ERROR',
            status_code=400
        )
    
    # Validar campos obrigatórios
    required_fields = ['title', 'image_url']
    missing_fields = validate_required_fields(data, required_fields)
    
    if missing_fields:
        return error_response(
            f'Campos obrigatórios ausentes: {", ".join(missing_fields)}',
            'VALIDATION_ERROR',
            {'missing_fields': missing_fields},
            status_code=400
        )
    
    # Verificar se o usuário existe
    user = User.query.get(g.current_user_id)
    if not user:
        return error_response(
            'Usuário não encontrado',
            'RESOURCE_NOT_FOUND',
            status_code=404
        )
    
    # Criar novo portal
    portal = Portal(
        title=data['title'],
        description=data.get('description'),
        image_url=data['image_url'],
        thumbnail_url=data.get('thumbnail_url'),
        creator_id=g.current_user_id,
        category_id=data.get('category_id'),
        location=data.get('location'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        is_public=data.get('is_public', True)
    )
    
    try:
        db.session.add(portal)
        db.session.flush()  # Para obter o ID do portal
        
        # Processar tags se fornecidas
        if 'tags' in data and data['tags']:
            for tag_name in data['tags']:
                tag_slug = create_slug(tag_name)
                tag = Tag.query.filter_by(slug=tag_slug).first()
                
                if not tag:
                    tag = Tag(name=tag_name, slug=tag_slug)
                    db.session.add(tag)
                
                portal.tags.append(tag)
        
        db.session.commit()
        return success_response({'portal': portal.to_dict()}, status_code=201)
    except Exception as e:
        db.session.rollback()
        return error_response(
            'Erro ao criar portal',
            'INTERNAL_ERROR',
            status_code=500
        )

@portals_bp.route('/portals/<int:portal_id>', methods=['PUT'])
@auth_required
def update_portal(portal_id):
    """
    Atualiza um portal
    """
    portal = Portal.query.get(portal_id)
    
    if not portal:
        return error_response(
            'Portal não encontrado',
            'RESOURCE_NOT_FOUND',
            status_code=404
        )
    
    # Verificar se o usuário é o criador do portal
    if g.current_user_id != portal.creator_id:
        return error_response(
            'Você só pode editar seus próprios portais',
            'AUTHORIZATION_ERROR',
            status_code=403
        )
    
    data = request.get_json()
    
    if not data:
        return error_response(
            'Dados JSON inválidos',
            'VALIDATION_ERROR',
            status_code=400
        )
    
    # Campos que podem ser atualizados
    updatable_fields = ['title', 'description', 'category_id', 'location', 'latitude', 'longitude', 'is_public']
    
    for field in updatable_fields:
        if field in data:
            setattr(portal, field, data[field])
    
    try:
        # Processar tags se fornecidas
        if 'tags' in data:
            # Limpar tags existentes
            portal.tags.clear()
            
            # Adicionar novas tags
            for tag_name in data['tags']:
                tag_slug = create_slug(tag_name)
                tag = Tag.query.filter_by(slug=tag_slug).first()
                
                if not tag:
                    tag = Tag(name=tag_name, slug=tag_slug)
                    db.session.add(tag)
                
                portal.tags.append(tag)
        
        db.session.commit()
        return success_response({'portal': portal.to_dict()})
    except Exception as e:
        db.session.rollback()
        return error_response(
            'Erro ao atualizar portal',
            'INTERNAL_ERROR',
            status_code=500
        )

@portals_bp.route('/portals/<int:portal_id>', methods=['DELETE'])
@auth_required
def delete_portal(portal_id):
    """
    Deleta um portal
    """
    portal = Portal.query.get(portal_id)
    
    if not portal:
        return error_response(
            'Portal não encontrado',
            'RESOURCE_NOT_FOUND',
            status_code=404
        )
    
    # Verificar se o usuário é o criador do portal
    if g.current_user_id != portal.creator_id:
        return error_response(
            'Você só pode deletar seus próprios portais',
            'AUTHORIZATION_ERROR',
            status_code=403
        )
    
    try:
        db.session.delete(portal)
        db.session.commit()
        return success_response(status_code=204)
    except Exception as e:
        db.session.rollback()
        return error_response(
            'Erro ao deletar portal',
            'INTERNAL_ERROR',
            status_code=500
        )

@portals_bp.route('/portals/<int:portal_id>/like', methods=['POST'])
@auth_required
def toggle_like_portal(portal_id):
    """
    Curte/descurte um portal (toggle)
    """
    portal = Portal.query.get(portal_id)
    
    if not portal:
        return error_response(
            'Portal não encontrado',
            'RESOURCE_NOT_FOUND',
            status_code=404
        )
    
    user = User.query.get(g.current_user_id)
    
    if not user:
        return error_response(
            'Usuário não encontrado',
            'RESOURCE_NOT_FOUND',
            status_code=404
        )
    
    # Verificar se já curtiu
    is_liked = portal in user.liked_portals
    
    try:
        if is_liked:
            # Descurtir
            user.liked_portals.remove(portal)
            action = 'removed'
        else:
            # Curtir
            user.liked_portals.append(portal)
            action = 'added'
        
        db.session.commit()
        
        return success_response({
            'action': action,
            'likes_count': len(portal.liked_by)
        })
    except Exception as e:
        db.session.rollback()
        return error_response(
            'Erro ao processar curtida',
            'INTERNAL_ERROR',
            status_code=500
        )

@portals_bp.route('/portals/<int:portal_id>/favorite', methods=['POST'])
@auth_required
def toggle_favorite_portal(portal_id):
    """
    Favorita/desfavorita um portal (toggle)
    """
    portal = Portal.query.get(portal_id)
    
    if not portal:
        return error_response(
            'Portal não encontrado',
            'RESOURCE_NOT_FOUND',
            status_code=404
        )
    
    user = User.query.get(g.current_user_id)
    
    if not user:
        return error_response(
            'Usuário não encontrado',
            'RESOURCE_NOT_FOUND',
            status_code=404
        )
    
    # Verificar se já favoritou
    is_favorited = portal in user.favorite_portals
    
    try:
        if is_favorited:
            # Desfavoritar
            user.favorite_portals.remove(portal)
            action = 'removed'
        else:
            # Favoritar
            user.favorite_portals.append(portal)
            action = 'added'
        
        db.session.commit()
        
        return success_response({
            'action': action,
            'favorites_count': len(portal.favorited_by)
        })
    except Exception as e:
        db.session.rollback()
        return error_response(
            'Erro ao processar favorito',
            'INTERNAL_ERROR',
            status_code=500
        )

