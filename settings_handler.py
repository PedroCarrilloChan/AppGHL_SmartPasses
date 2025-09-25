import os
import requests
import json
from flask import Blueprint, request, jsonify, render_template

# -----------------------------------------------------------------------------
# PASO 1: CREAR EL BLUEPRINT (LA CAJA DE HERRAMIENTAS)
# -----------------------------------------------------------------------------
# Esta línea DEBE estar antes de cualquier @settings_bp.route
settings_bp = Blueprint('settings', __name__)

# -----------------------------------------------------------------------------
# FUNCIÓN AUXILIAR PARA COMUNICARSE CON CLOUDFLARE D1
# -----------------------------------------------------------------------------
def query_d1(sql, params=[]):
    """
    Ejecuta una consulta SQL en la base de datos D1 a través de la API de Cloudflare.
    """
    account_id = os.environ.get('CF_ACCOUNT_ID')
    db_id = os.environ.get('CF_D1_DATABASE_ID')
    api_token = os.environ.get('CF_API_TOKEN')

    if not all([account_id, db_id, api_token]):
        print("🚨 ERROR: Faltan secretos de Cloudflare (CF_ACCOUNT_ID, CF_D1_DATABASE_ID, CF_API_TOKEN).")
        return None, ("Faltan secretos de configuración del servidor.", 500)

    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{db_id}/query"
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
    data = {"sql": sql, "params": params}

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.HTTPError as err:
        print(f"Error en la API de D1: {err.response.text}")
        return None, (err.response.text, err.response.status_code)

# -----------------------------------------------------------------------------
# PASO 2: USAR EL BLUEPRINT PARA DEFINIR LAS RUTAS
# -----------------------------------------------------------------------------
@settings_bp.route('/settings', methods=['GET'])
def settings_page():
    """
    Muestra la página de configuración (settings.html).
    """
    location_id = request.args.get('locationId')
    print(f"DEBUG: locationId recibido en la URL: {location_id}") # Mensaje de depuración
    if not location_id:
        # Aunque GHL no lo envíe, no queremos que la app falle, solo que el campo esté vacío.
        location_id = "" 
    return render_template('settings.html', location_id=location_id)


@settings_bp.route('/settings/save', methods=['POST'])
def save_settings():
    """
    Recibe los datos del formulario de configuración y los guarda en la base de datos D1.
    """
    data = request.get_json()
    location_id = data.get('locationId')
    api_key = data.get('apiKey')
    program_id = data.get('programId')

    if not location_id or location_id == 'None' or location_id == '':
        print(f"🚨 ERROR CRÍTICO: Se intentó guardar credenciales sin un Location ID válido.")
        return jsonify({"error": "Location ID is missing. Please check your app configuration in the GHL Marketplace."}), 400

    if not all([api_key, program_id]):
        return jsonify({"error": "Faltan campos obligatorios (API Key o Program ID)."}), 400

    print(f"--- Guardando credenciales para {location_id} ---") # Mensaje de depuración
    print(f"Datos: {data}") # Mensaje de depuración

    sql = "INSERT OR REPLACE INTO sub_account_credentials (location