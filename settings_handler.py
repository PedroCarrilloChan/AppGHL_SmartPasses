# settings_handler.py
# Maneja la página de configuración y el guardado de credenciales.

from flask import Blueprint, request, jsonify, render_template

settings_bp = Blueprint('settings_handler', __name__)

# Simulación de una base de datos.
credentials_db = {}

@settings_bp.route('/settings')
def settings_page():
    """Muestra la página de configuración a la agencia."""
    # 1. Obtener locationId de los parámetros de la URL que envía GHL
    location_id = request.args.get('locationId')

    # Debug: Imprimir para ver qué llega
    print(f"DEBUG: locationId recibido en la URL: {location_id}")

    # 2. Pasar el locationId al template HTML
    # La plantilla 'settings.html' ahora podrá acceder a esta variable.
    return render_template('settings.html', location_id=location_id)

@settings_bp.route('/settings/save', methods=['POST'])
def save_settings():
    """Recibe y guarda las credenciales de la agencia."""
    data = request.json
    location_id = data.get('locationId')
    api_key = data.get('apiKey')
    program_id = data.get('programId')

    print(f"DEBUG: Datos recibidos para guardar: {data}")

    if not all([location_id, api_key, program_id]):
        return jsonify({"error": "Missing required fields."}), 400

    credentials_db[location_id] = {
        "smartpasses_api_key": api_key,
        "default_program_id": program_id
    }

    print(f"--- CREDENCIALES GUARDADAS PARA {location_id} ---")
    return jsonify({"status": "success"}), 200
