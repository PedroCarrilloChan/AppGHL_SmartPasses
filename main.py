# main.py
# Archivo principal que inicia el servidor y registra todas las rutas.

from flask import Flask

# Importar los "Blueprints" de nuestros otros archivos
from auth_handler import auth_bp
from actions.customer import customer_actions_bp
from actions.program import program_actions_bp
from actions.offer import offer_actions_bp
from webhook_handler import webhook_bp
from settings_handler import settings_bp # <-- NUEVA LÍNEA

# Crear la aplicación principal de Flask
app = Flask(__name__)

# Registrar los Blueprints en la aplicación principal
app.register_blueprint(auth_bp)
app.register_blueprint(customer_actions_bp)
app.register_blueprint(program_actions_bp)
app.register_blueprint(offer_actions_bp)
app.register_blueprint(webhook_bp)
app.register_blueprint(settings_bp) # <-- NUEVA LÍNEA

# --- Endpoint de bienvenida ---
@app.route('/')
def index():
    return "El servidor intermediario de Smart Passes para GHL está funcionando."

# --- Ejecutar el servidor ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
