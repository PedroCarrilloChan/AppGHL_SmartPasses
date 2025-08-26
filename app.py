import os
from flask import Flask
from config import config

# Importar los blueprints
from auth_handler import auth_bp
from actions.customer import customer_actions_bp
from actions.program import program_actions_bp
from webhook_handler import webhook_bp
from settings_handler import settings_bp # <-- LÍNEA AÑADIDA

def create_app(config_name=None):
    """Factory function para crear la aplicación Flask"""

    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'production')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Inicializar configuración específica del entorno
    config[config_name].init_app(app)

    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_actions_bp)
    app.register_blueprint(program_actions_bp)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(settings_bp) # <-- LÍNEA AÑADIDA

    # Endpoint de salud para el servidor
    @app.route('/health')
    def health_check():
        return {"status": "healthy", "service": "SmartPasses GHL Bridge"}, 200

    # Endpoint de bienvenida
    @app.route('/')
    def index():
        return "El servidor intermediario de Smart Passes para GHL está funcionando."

    return app

# Para desarrollo local
if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=5000, debug=True)