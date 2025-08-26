# settings_handler.py
# Maneja la página de configuración y el guardado de credenciales.

from flask import Blueprint, request, jsonify, render_template

settings_bp = Blueprint('settings_handler', __name__)

# --- RUTA DE PRUEBA AÑADIDA ---
# Esta ruta simple nos ayudará a confirmar si el blueprint se registra correctamente.
@settings_bp.route('/')
def test_route():
    return "El Blueprint de Settings está funcionando!"
# ------------------------------------


# Simulación de una base de datos. En una app real, usarías una base de datos real.
credentials_db = {}

@settings_bp.route('/settings')
def settings_page():
    """Muestra la página de configuración a la agencia."""
    return render_template('settings.html')

@settings_bp.route('/settings/save', methods=['POST'])
def save_settings():
    """Recibe y guarda las credenciales de la agencia."""
    data = request.json
    location_id = data.get('locationId')
    api_key = data.get('apiKey')
    program_id = data.get('programId')

    if not all([location_id, api_key, program_id]):
        return jsonify({"error": "Missing required fields."}), 400

    # Guardamos las credenciales asociadas al ID de la sub-cuenta
    credentials_db[location_id] = {
        "smartpasses_api_key": api_key,
        "default_program_id": program_id
    }

    print("--- CREDENCIALES GUARDADAS ---")
    print(f"Location ID: {location_id}")
    print(f"Datos Guardados: {credentials_db[location_id]}")
    print("----------------------------")

    return jsonify({"status": "success"}), 200