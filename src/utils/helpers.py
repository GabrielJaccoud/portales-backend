import re
from datetime import datetime
from flask import jsonify

def create_slug(text):
    """
    Cria um slug a partir de um texto
    """
    # Converter para minúsculas e remover acentos
    text = text.lower()
    # Substituir espaços e caracteres especiais por hífens
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # Remover hífens do início e fim
    text = text.strip('-')
    return text

def success_response(data=None, message=None, status_code=200):
    """
    Cria uma resposta de sucesso padronizada
    """
    response = {'success': True}
    
    if data is not None:
        if isinstance(data, dict):
            response.update(data)
        else:
            response['data'] = data
    
    if message:
        response['message'] = message
    
    return jsonify(response), status_code

def error_response(error_message, error_code=None, details=None, status_code=400):
    """
    Cria uma resposta de erro padronizada
    """
    response = {
        'success': False,
        'error': error_message,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    if error_code:
        response['error_code'] = error_code
    
    if details:
        response['details'] = details
    
    return jsonify(response), status_code

def validate_required_fields(data, required_fields):
    """
    Valida se os campos obrigatórios estão presentes nos dados
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    return missing_fields

def paginate_query(query, page=1, per_page=20, max_per_page=100):
    """
    Aplica paginação a uma query SQLAlchemy
    """
    # Limitar per_page ao máximo permitido
    per_page = min(per_page, max_per_page)
    
    # Executar a paginação
    paginated = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return {
        'items': paginated.items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': paginated.total,
            'pages': paginated.pages,
            'has_next': paginated.has_next,
            'has_prev': paginated.has_prev
        }
    }

