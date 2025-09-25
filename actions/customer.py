import os
import requests
import json
from flask import Blueprint, request, jsonify

# Crea el Blueprint para este módulo
customer_actions_bp = Blueprint('customer_actions', __name__)

# URL base de la API de SmartPasses
SMARTPASSES_API_BASE_URL = "https://pass.smartpasses.io/api/v1/loyalty"

# -----------------------------------------------------------------------------
# FUNCIÓN AUXILIAR PARA COMUNICARSE CON CLOUDFLARE D1
# -----------------------------------------------------------------------------
def query_d1(sql, params=[]):
    """
    Ejecuta una consulta SQL en la base de datos D1 a través de la API de Cloudflare.
    Lee las credenciales necesarias desde los Secrets de Replit.
    """
    account_id = os.environ.get('CF_ACCOUNT_ID')
    db_id = os.environ.get('CF_D1_DATABASE_ID')
    api_token = os.environ.get('CF_API_TOKEN')

    if not all([account_id, db_id, api_token]):
        print("🚨 ERROR: Faltan secretos de Cloudflare en Replit (CF_ACCOUNT_ID, CF_D1_DATABASE_ID, CF_API_TOKEN).")
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
# FUNCIÓN AUXILIAR PARA OBTENER CREDENCIALES
# -----------------------------------------------------------------------------
def get_agency_credentials(ghl_data):
    """
    Obtiene las credenciales de la agencia desde la base de datos D1
    basándose en el 'locationId' proporcionado por GHL.
    """
    location_id = ghl_data.get('locationId') or ghl_data.get('location_id')

    if not location_id:
        return None, {"error": "No se recibió el Location ID de la sub-cuenta."}, 400

    # Sentencia SQL para seleccionar las credenciales de la sub-cuenta actual
    sql = "SELECT api_key, program_id FROM sub_account_credentials WHERE location_id = ?;"
    params = [location_id]

    # Ejecuta la consulta para obtener los datos
    result, error = query_d1(sql, params)

    if error:
        print(f"🚨 ERROR al leer de D1: {error[0]}")
        return None, {"error": "No se pudieron obtener las credenciales desde la base de datos."}, error[1]

    # La API de D1 devuelve los resultados en una lista dentro de la clave 'results'
    if result and result.get('results'):
        db_row = result['results'][0]
        credentials = {
            "smartpasses_api_key": db_row['api_key'],
            "default_program_id": db_row['program_id']
        }
        return credentials, None, None
    else:
        # Esto ocurre si el usuario aún no ha guardado su configuración
        print(f"🔎 No se encontraron credenciales en D1 para Location ID: {location_id}.")
        return None, {"error": "La aplicación no ha sido configurada. Por favor, guarde sus credenciales."}, 400

# -----------------------------------------------------------------------------
# RUTAS DE LAS ACCIONES DE GHL
# -----------------------------------------------------------------------------

@customer_actions_bp.route('/actions/create_customer', methods=['POST'])
def handle_create_customer():
    ghl_data = request.json
    print(f"📥 Datos recibidos de GHL (create_customer): {json.dumps(ghl_data, indent=2)}")

    agency_credentials, error_response, status_code = get_agency_credentials(ghl_data)
    if error_response:
        return jsonify(error_response), status_code

    inputs = ghl_data.get('inputs', {})
    smartpasses_api_key = agency_credentials.get('smartpasses_api_key')
    program_id = inputs.get('program_id') or agency_credentials.get('default_program_id')
    email = inputs.get('contact_email')

    if not program_id or not email:
        return jsonify({"error": "El Program ID y el Email son obligatorios."}), 400

    create_url = f"{SMARTPASSES_API_BASE_URL}/programs/{program_id}/customers"
    payload = {
        "firstName": inputs.get('contact_first_name', ''),
        "lastName": inputs.get('contact_last_name', ''),
        "email": email,
        "phone": inputs.get('contact_phone', '')
    }
    headers = {"Authorization": smartpasses_api_key, "Content-Type": "application/json"}

    try:
        response = requests.post(create_url, json=payload, headers=headers)
        response.raise_for_status()
        return jsonify(response.json()), 200
    except requests.exceptions.HTTPError as err:
        return jsonify({"error": "Fallo en la API de Smart Passes", "details": err.response.text}), err.response.status_code
    except Exception as e:
        return jsonify({"error": "Error interno del servidor.", "details": str(e)}), 500

# Aquí puedes agregar el resto de tus acciones (add_points, get_customer, etc.)
# Todas seguirán el mismo patrón:
# 1. Obtener ghl_data
# 2. Llamar a get_agency_credentials(ghl_data)
# 3. Usar las credenciales para hacer la llamada a la API de SmartPasses