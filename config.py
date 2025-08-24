
import os
from datetime import timedelta

class Config:
    """Configuración base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración de la aplicación
    DEBUG = False
    TESTING = False
    
    # Configuración de la base de datos
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # APIs de terceros
    SMARTPASSES_API_KEY = os.environ.get('SMARTPASSES_API_KEY')
    GHL_CLIENT_ID = os.environ.get('GHL_CLIENT_ID')
    GHL_CLIENT_SECRET = os.environ.get('GHL_CLIENT_SECRET')
    GHL_SHARED_SECRET = os.environ.get('GHL_SHARED_SECRET')
    
    # Configuración del servidor
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    
    # En producción, asegúrate de que estas variables estén configuradas
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Log de errores a archivo
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            file_handler = RotatingFileHandler('logs/smartpasses.log', maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('SmartPasses Smart Passes Server startup')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
