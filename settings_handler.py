# settings_handler.py
# Maneja la página de configuración y el guardado de credenciales.

from flask import Blueprint, request, jsonify, render_template

settings_bp = Blueprint('settings_handler', __name__)

# Simulación de una base de datos. La hacemos accesible globalmente.
# En una app real, esto sería una conexión a una base de datos real (PostgreSQL, MongoDB, etc.).
credentials_db = {}

@settings_bp.route('/settings')
def settings_page():
    """Muestra la página de configuración a la agencia."""
    location_id = request.args.get('locationId')
    print(f"DEBUG: locationId recibido en la URL: {location_id}")
    return render_template('settings.html', location_id=location_id)

@settings_bp.route('/settings/save', methods=['POST'])
def save_settings():
    """Recibe y guarda las credenciales de la agencia."""
    data = request.json
    location_id = data.get('locationId')
    api_key = data.get('apiKey')
    program_id = data.get('programId')

    if not all([location_id, api_key, program_id]):
        return jsonify({"error": "Missing required fields."}), 400

    credentials_db[location_id] = {
        "smartpasses_api_key": api_key,
        "default_program_id": program_id
    }

    print(f"--- CREDENCIALES GUARDADAS PARA {location_id} ---")
    print(f"Datos: {credentials_db[location_id]}")
    return jsonify({"status": "success"}), 200
