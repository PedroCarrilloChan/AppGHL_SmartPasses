import os
import requests
import json
from flask import Blueprint, request, jsonify, render_template

# Crea el Blueprint para este módulo
settings_bp = Blueprint('settings', __name__)

# -----------------------------------------------------------------------------
# FUNCIÓN AUXILIAR PARA COMUNICARSE CON CLOUDFLARE D1
# -----------------------------------------------------------------------------
def query_d1(sql, params=[]):
    """
    Ejecuta una consulta SQL en la base de datos D1 a través de la API de Cloudflare.
    Lee las credenciales necesarias desde los Secrets de Replit.
    """
    # Lee las credenciales desde los Secrets de Replit
    account_id = os.environ.get('CF_ACCOUNT_ID')
    db_id = os.environ.get('CF_D1_DATABASE_ID')
    api_token = os.environ.get('CF_API_TOKEN')

    # Valida que todos los secretos estén configurados
    if not all([account_id, db_id, api_token]):
        print("🚨 ERROR: Faltan secretos de Cloudflare en Replit (CF_ACCOUNT_ID, CF_D1_DATABASE_ID, CF_API_TOKEN).")
        return None, ("Faltan secretos de configuración del servidor.", 500)

    # Construye la URL de la API y los encabezados
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{db_id}/query"
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
    data = {"sql": sql, "params": params}

    try:
        # Realiza la petición a la API
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Lanza un error si la respuesta no es exitosa (código 2xx)
        return response.json(), None
    except requests.exceptions.HTTPError as err:
        # Devuelve el texto del error y el código de estado para una mejor depuración
        print(f"Error en la API de D1: {err.response.text}")
        return None, (err.response.text, err.response.status_code)

# -----------------------------------------------------------------------------
# RUTAS DEL SERVIDOR
# -----------------------------------------------------------------------------
@settings_bp.route('/settings', methods=['GET'])
def settings_page():
    """
    Muestra la página de configuración (settings.html).
    Obtiene el 'locationId' de la URL y lo pasa a la plantilla.
    """
    location_id = request.args.get('locationId')
    if not location_id:
        return "Error: Falta el Location ID en la URL. Acceda a esta página desde GHL.", 400
    # Renderiza el archivo 'settings.html' y le inyecta la variable 'location_id'
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

    if not all([location_id, api_key, program_id]):
        return jsonify({"error": "Faltan campos obligatorios."}), 400

    # Sentencia SQL para insertar un nuevo registro o reemplazarlo si ya existe (upsert)
    sql = "INSERT OR REPLACE INTO sub_account_credentials (location_id, api_key, program_id) VALUES (?, ?, ?);"
    params = [location_id, api_key, program_id]

    # Ejecuta la consulta para guardar los datos
    result, error = query_d1(sql, params)

    if error:
        print(f"🚨 ERROR al guardar en D1: {error[0]}")
        return jsonify({"error": "No se pudieron guardar las credenciales en la base de datos."}), error[1]

    print(f"✅ Credenciales guardadas en Cloudflare D1 para Location ID: {location_id}")
    return jsonify({"status": "success", "message": "Configuración guardada exitosamente."}), 200