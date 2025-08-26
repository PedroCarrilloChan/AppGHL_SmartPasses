# actions/customer.py
# Contiene la lógica para todas las acciones de GHL relacionadas con los clientes.

from flask import Blueprint, request, jsonify
import requests
import os
import json
# Importamos la base de datos simulada desde el otro archivo
from settings_handler import credentials_db

customer_actions_bp = Blueprint('customer_actions', __name__)

SMARTPASSES_API_BASE_URL = "https://pass.smartpasses.io/api/v1/loyalty"

def get_agency_credentials(ghl_data):
    """
    Función auxiliar para obtener las credenciales de la agencia
    basado en el locationId que envía GHL.
    """
    location_id = ghl_data.get('locationId')
    if not location_id:
        return None, {"error": "No se recibió el Location ID de la sub-cuenta."}, 400

    agency_credentials = credentials_db.get(location_id)
    if not agency_credentials:
        return None, {"error": "La aplicación no ha sido configurada. Por favor, guarde sus credenciales en la página de configuración de la app."}, 400

    return agency_credentials, None, None

@customer_actions_bp.route('/actions/create_customer', methods=['POST'])
def handle_create_customer():
    ghl_data = request.json
    print(f"📥 Datos recibidos de GHL (create_customer): {json.dumps(ghl_data, indent=2)}")

    agency_credentials, error_response, status_code = get_agency_credentials(ghl_data)
    if error_response:
        return jsonify(error_response), status_code

    smartpasses_api_key = agency_credentials.get('smartpasses_api_key')
    program_id = ghl_data.get('program_id') or agency_credentials.get('default_program_id')
    email = ghl_data.get('contact_email')

    if not program_id or not email:
        return jsonify({"error": "El Program ID y el Email son obligatorios."}), 400

    create_url = f"{SMARTPASSES_API_BASE_URL}/programs/{program_id}/customers"
    payload = {
        "firstName": ghl_data.get('contact_first_name'),
        "lastName": ghl_data.get('contact_last_name'),
        "email": email,
        "phone": ghl_data.get('contact_phone')
    }
    headers = {
        "Authorization": smartpasses_api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(create_url, json=payload, headers=headers)
        response.raise_for_status()
        smartpasses_response = response.json()
        return jsonify(smartpasses_response), 200
    except requests.exceptions.HTTPError as err:
        return jsonify({
            "error": "Fallo en la comunicación con la API de Smart Passes", 
            "details": err.response.text
        }), err.response.status_code
    except Exception as e:
        return jsonify({"error": "Ocurrió un error interno en el servidor."}), 500

@customer_actions_bp.route('/actions/add_points', methods=['POST'])
def handle_add_points():
    ghl_data = request.json
    print(f"📥 Datos recibidos de GHL (add_points): {json.dumps(ghl_data, indent=2)}")

    agency_credentials, error_response, status_code = get_agency_credentials(ghl_data)
    if error_response:
        return jsonify(error_response), status_code

    smartpasses_api_key = agency_credentials.get('smartpasses_api_key')
    program_id = ghl_data.get('program_id') or agency_credentials.get('default_program_id')
    customer_id = ghl_data.get('customer_id')
    points_to_add = ghl_data.get('points_to_add')

    if not all([program_id, customer_id, points_to_add]):
        return jsonify({"error": "Program ID, Customer ID, y Points to Add son obligatorios."}), 400

    add_points_url = f"{SMARTPASSES_API_BASE_URL}/programs/{program_id}/customers/{customer_id}/points/add"
    payload = {"points": int(points_to_add)}
    headers = {"Authorization": smartpasses_api_key, "Content-Type": "application/json"}

    try:
        response = requests.post(add_points_url, json=payload, headers=headers)
        response.raise_for_status()
        smartpasses_response = response.json()
        return jsonify(smartpasses_response), 200
    except requests.exceptions.HTTPError as err:
        return jsonify({"error": "Fallo al añadir puntos", "details": err.response.text}), err.response.status_code
    except Exception as e:
        return jsonify({"error": "Ocurrió un error interno en el servidor."}), 500

@customer_actions_bp.route('/actions/get_customer', methods=['POST'])
def handle_get_customer():
    ghl_data = request.json
    print(f"📥 Datos recibidos de GHL (get_customer): {json.dumps(ghl_data, indent=2)}")

    agency_credentials, error_response, status_code = get_agency_credentials(ghl_data)
    if error_response:
        return jsonify(error_response), status_code

    smartpasses_api_key = agency_credentials.get('smartpasses_api_key')
    program_id = ghl_data.get('program_id') or agency_credentials.get('default_program_id')
    customer_id = ghl_data.get('customer_id')

    if not all([program_id, customer_id]):
        return jsonify({"error": "Program ID y Customer ID son obligatorios."}), 400

    get_customer_url = f"{SMARTPASSES_API_BASE_URL}/programs/{program_id}/customers/{customer_id}"
    headers = {"Authorization": smartpasses_api_key}

    try:
        response = requests.get(get_customer_url, headers=headers)
        response.raise_for_status()
        smartpasses_response = response.json()
        return jsonify(smartpasses_response), 200
    except requests.exceptions.HTTPError as err:
        return jsonify({"error": "Fallo al obtener el cliente", "details": err.response.text}), err.response.status_code
    except Exception as e:
        return jsonify({"error": "Ocurrió un error interno en el servidor."}), 500

@customer_actions_bp.route('/actions/update_customer', methods=['POST'])
def handle_update_customer():
    ghl_data = request.json
    print(f"📥 Datos recibidos de GHL (update_customer): {json.dumps(ghl_data, indent=2)}")

    agency_credentials, error_response, status_code = get_agency_credentials(ghl_data)
    if error_response:
        return jsonify(error_response), status_code

    smartpasses_api_key = agency_credentials.get('smartpasses_api_key')
    program_id = ghl_data.get('program_id') or agency_credentials.get('default_program_id')
    customer_id = ghl_data.get('customer_id')

    if not all([program_id, customer_id]):
        return jsonify({"error": "Program ID y Customer ID son obligatorios."}), 400

    payload = {}
    if ghl_data.get('first_name'): payload['firstName'] = ghl_data.get('first_name')
    if ghl_data.get('last_name'): payload['lastName'] = ghl_data.get('last_name')
    if ghl_data.get('email'): payload['email'] = ghl_data.get('email')
    if ghl_data.get('phone'): payload['phone'] = ghl_data.get('phone')
    if ghl_data.get('points') is not None: payload['points'] = int(ghl_data.get('points'))

    if not payload:
        return jsonify({"error": "Debes proporcionar al menos un campo para actualizar."}), 400

    update_customer_url = f"{SMARTPASSES_API_BASE_URL}/programs/{program_id}/customers/{customer_id}"
    headers = {"Authorization": smartpasses_api_key, "Content-Type": "application/json"}

    try:
        response = requests.put(update_customer_url, json=payload, headers=headers)
        response.raise_for_status()
        smartpasses_response = response.json()
        return jsonify(smartpasses_response), 200
    except requests.exceptions.HTTPError as err:
        return jsonify({"error": "Fallo al actualizar el cliente", "details": err.response.text}), err.response.status_code
    except Exception as e:
        return jsonify({"error": "Ocurrió un error interno en el servidor."}), 500

@customer_actions_bp.route('/actions/delete_customer', methods=['POST'])
def handle_delete_customer():
    ghl_data = request.json
    print(f"📥 Datos recibidos de GHL (delete_customer): {json.dumps(ghl_data, indent=2)}")

    agency_credentials, error_response, status_code = get_agency_credentials(ghl_data)
    if error_response:
        return jsonify(error_response), status_code

    smartpasses_api_key = agency_credentials.get('smartpasses_api_key')
    program_id = ghl_data.get('program_id') or agency_credentials.get('default_program_id')
    customer_id = ghl_data.get('customer_id')

    if not all([program_id, customer_id]):
        return jsonify({"error": "Program ID y Customer ID son obligatorios."}), 400

    delete_customer_url = f"{SMARTPASSES_API_BASE_URL}/programs/{program_id}/customers/{customer_id}"
    headers = {"Authorization": smartpasses_api_key}

    try:
        response = requests.delete(delete_customer_url, headers=headers)
        response.raise_for_status()
        return jsonify({"status": "success", "message": "Customer deleted successfully"}), 200
    except requests.exceptions.HTTPError as err:
        return jsonify({"error": "Fallo al borrar el cliente", "details": err.response.text}), err.response.status_code
    except Exception as e:
        return jsonify({"error": "Ocurrió un error interno en el servidor."}), 500
