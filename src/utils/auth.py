import firebase_admin
from firebase_admin import credentials, auth
from flask import request, jsonify, g
from functools import wraps
import os

# Inicializar Firebase Admin SDK
# Em produção, você deve usar um arquivo de credenciais do Firebase
# Por enquanto, vamos usar uma configuração mock para desenvolvimento
try:
    # Tentar inicializar com credenciais padrão (se disponível)
    firebase_admin.initialize_app()
except Exception as e:
    print(f"Firebase não inicializado: {e}")
    print("Usando modo de desenvolvimento sem Firebase")

def verify_firebase_token(token):
    """
    Verifica o token Firebase JWT
    Em desenvolvimento, retorna um usuário mock
    """
    try:
        # Em produção, descomente esta linha:
        # decoded_token = auth.verify_id_token(token)
        # return decoded_token['uid']
        
        # Para desenvolvimento, vamos simular a verificação
        if token == "mock_token":
            return "mock_user_id"
        elif token.startswith("user_"):
            return token
        else:
            return None
    except Exception as e:
        print(f"Erro ao verificar token: {e}")
        return None

def auth_required(f):
    """
    Decorador para endpoints que requerem autenticação
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'success': False,
                'error': 'Token de autorização ausente',
                'error_code': 'AUTHENTICATION_ERROR'
            }), 401
        
        try:
            # Extrair token do header "Bearer <token>"
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({
                'success': False,
                'error': 'Formato de token inválido',
                'error_code': 'AUTHENTICATION_ERROR'
            }), 401
        
        user_id = verify_firebase_token(token)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Token inválido ou expirado',
                'error_code': 'AUTHENTICATION_ERROR'
            }), 401
        
        # Armazenar o user_id no contexto da requisição
        g.current_user_id = user_id
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_auth(f):
    """
    Decorador para endpoints onde a autenticação é opcional
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(' ')[1]
                user_id = verify_firebase_token(token)
                g.current_user_id = user_id
            except:
                g.current_user_id = None
        else:
            g.current_user_id = None
        
        return f(*args, **kwargs)
    
    return decorated_function

