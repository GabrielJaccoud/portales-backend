import os
import sys
from flask import Flask, send_from_directory, request, g
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.portals import portals_bp
from src.routes.categories import categories_bp
from src.routes.reviews import reviews_bp
from src.routes.explorations import explorations_bp
from src.routes.health import health_bp
from src.routes.search import search_bp
from src.routes.analytics import analytics_bp
from src.utils.helpers import error_response
import logging
import json
from datetime import datetime

# DON\'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "service": "portales-api",
            "module": record.name,
            "function": record.funcName,
        }
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)
        if record.stack_info:
            log_record['stack_info'] = self.formatStack(record.stack_info)
        if hasattr(record, 'details'):
            log_record['details'] = record.details

        return json.dumps(log_record)

def configure_logging(app):
    handler = logging.StreamHandler()
    formatter = JsonFormatter()
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO) # Default level

    # Remove default Flask handlers
    for h in list(app.logger.handlers): # Iterate over a copy
        app.logger.removeHandler(h)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
CORS(app) # Habilitar CORS para todas as rotas

app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Configurar logging
configure_logging(app)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(portals_bp, url_prefix='/api')
app.register_blueprint(categories_bp, url_prefix='/api')
app.register_blueprint(reviews_bp, url_prefix='/api')
app.register_blueprint(explorations_bp, url_prefix='/api')
app.register_blueprint(health_bp, url_prefix='/api')
app.register_blueprint(search_bp, url_prefix='/api')
app.register_blueprint(analytics_bp, url_prefix='/api')

# Configurar banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

# Middleware para adicionar request_id e user_id aos logs
@app.before_request
def before_request():
    g.request_id = request.headers.get('X-Request-ID', os.urandom(8).hex())
    # g.current_user_id é definido pelo decorador auth_required/optional_auth

@app.after_request
def after_request(response):
    response.headers['X-Request-ID'] = g.request_id
    return response

# Tratamento de erros global
@app.errorhandler(404)
def not_found_error(error):
    return error_response('Recurso não encontrado', 'RESOURCE_NOT_FOUND', status_code=404)

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error('Erro interno do servidor', exc_info=True, extra={'request_id': g.request_id})
    return error_response('Erro interno do servidor', 'INTERNAL_ERROR', status_code=500)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


