# actions/customer.py
# Contiene la lógica para todas las acciones de GHL relacionadas con los clientes.

from flask import Blueprint, request, jsonify
import requests
import os
import json

# Crear un "Blueprint". Es como un mini-servidor para organizar nuestras rutas.
customer_actions_bp = Blueprint('customer_actions', __name__)

SMARTPASSES_API_BASE_URL = "https://pass.smartpasses.io/api/v1/loyalty"

@customer_actions_bp.route('/actions/create_customer', methods=['POST'])
def handle_create_customer():
    ghl_data = request.json
    print(f"📥 Datos recibidos de GHL (create_customer): {json.dumps(ghl_data, indent=2)}")

    smartpasses_api_key = os.environ.get('SMARTPASSES_API_KEY')
    if not smartpasses_api_key:
        print("❌ ERROR: La SMARTPASSES_API_KEY no está configurada.")
        return jsonify({"error": "Configuración del servidor incompleta."}), 500

    program_id = ghl_data.get('program_id')
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
        print(f"🚀 Enviando payload a SmartPasses: {json.dumps(payload, indent=2)}")
        response = requests.post(create_url, json=payload, headers=headers)
        response.raise_for_status()
        smartpasses_response = response.json()
        print(f"✅ Respuesta COMPLETA de SmartPasses: {json.dumps(smartpasses_response, indent=2)}")

        customer_id = smartpasses_response.get("id")
        if not customer_id:
            raise Exception("La API no devolvió un ID de cliente.")

        card_data = None
        card_list = smartpasses_response.get("card")

        if isinstance(card_list, list) and len(card_list) > 0:
            card_data = card_list[0]
        elif isinstance(card_list, dict):
            card_data = card_list

        response_data = {
            "customer_id": customer_id,
            "status": "success"
        }

        if card_data:
            response_data.update({
                "pass_url": card_data.get("url"),
                "serial_number": card_data.get("serialNumber"),
                "pass_type_identifier": card_data.get("passTypeIdentifier")
            })

        print(f"📤 Enviando respuesta final a GHL: {json.dumps(response_data, indent=2)}")
        return jsonify(response_data), 200

    except requests.exceptions.HTTPError as err:
        error_details = err.response.text
        print(f"❌ Error HTTP de SmartPasses: {error_details}")
        return jsonify({
            "error": "Fallo en la comunicación con la API de Smart Passes", 
            "details": error_details
        }), err.response.status_code
    except Exception as e:
        print(f"💥 Error inesperado en create_customer: {str(e)}")
        return jsonify({"error": "Ocurrió un error interno en el servidor."}), 500


@customer_actions_bp.route('/actions/add_points', methods=['POST'])
def handle_add_points():
    ghl_data = request.json
    print(f"📥 Datos recibidos de GHL (add_points): {json.dumps(ghl_data, indent=2)}")

    smartpasses_api_key = os.environ.get('SMARTPASSES_API_KEY')
    if not smartpasses_api_key:
        print("❌ ERROR: La SMARTPASSES_API_KEY no está configurada.")
        return jsonify({"error": "Configuración del servidor incompleta."}), 500

    program_id = ghl_data.get('program_id')
    customer_id = ghl_data.get('customer_id')
    points_to_add = ghl_data.get('points_to_add')

    if not all([program_id, customer_id, points_to_add]):
        return jsonify({"error": "Program ID, Customer ID, y Points to Add son obligatorios."}), 400

    add_points_url = f"{SMARTPASSES_API_BASE_URL}/programs/{program_id}/customers/{customer_id}/points/add"

    payload = { "points": int(points_to_add) }
    headers = { "Authorization": smartpasses_api_key, "Content-Type": "application/json" }

    try:
        print(f"🚀 Enviando payload a SmartPasses: {json.dumps(payload, indent=2)}")
        response = requests.post(add_points_url, json=payload, headers=headers)
        response.raise_for_status()

        smartpasses_response = response.json()
        print(f"✅ Puntos añadidos exitosamente: {json.dumps(smartpasses_response, indent=2)}")

        return jsonify({
            "new_point_total": smartpasses_response.get("points"),
            "status": "success"
        }), 200

    except requests.exceptions.HTTPError as err:
        error_details = err.response.text
        print(f"❌ Error HTTP de SmartPasses: {error_details}")
        return jsonify({
            "error": "Fallo en la comunicación con la API de Smart Passes", 
            "details": error_details
        }), err.response.status_code
    except Exception as e:
        print(f"💥 Error inesperado en add_points: {str(e)}")
        return jsonify({"error": "Ocurrió un error interno en el servidor."}), 500

# Pega este nuevo bloque de código al final de tu archivo actions/customer.py

@customer_actions_bp.route('/actions/get_customer', methods=['POST'])
def handle_get_customer():
    """
    Esta función se activa cuando un workflow de GHL ejecuta la acción "Get a Customer".
    """
    ghl_data = request.json
    print(f"📥 Datos recibidos de GHL (get_customer): {json.dumps(ghl_data, indent=2)}")

    smartpasses_api_key = os.environ.get('SMARTPASSES_API_KEY')
    if not smartpasses_api_key:
        print("❌ ERROR: La SMARTPASSES_API_KEY no está configurada.")
        return jsonify({"error": "Configuración del servidor incompleta."}), 500

    # Extraemos los datos usando las "Reference keys" que definimos en GHL
    program_id = ghl_data.get('program_id')
    customer_id = ghl_data.get('customer_id')

    if not all([program_id, customer_id]):
        return jsonify({"error": "Program ID y Customer ID son obligatorios."}), 400

    # Preparar la petición GET para la API de Smart Passes
    get_customer_url = f"{SMARTPASSES_API_BASE_URL}/programs/{program_id}/customers/{customer_id}"

    headers = {
        "Authorization": smartpasses_api_key
    }

    try:
        print(f"🚀 Solicitando información del cliente a SmartPasses...")
        response = requests.get(get_customer_url, headers=headers)
        response.raise_for_status()

        smartpasses_response = response.json()
        print(f"✅ Información obtenida exitosamente: {json.dumps(smartpasses_response, indent=2)}")

        # Devolvemos la respuesta completa a GHL para usarla en variables personalizadas
        return jsonify(smartpasses_response), 200

    except requests.exceptions.HTTPError as err:
        error_details = err.response.text
        print(f"❌ Error HTTP de SmartPasses: {error_details}")
        return jsonify({
            "error": "Fallo en la comunicación con la API de Smart Passes", 
            "details": error_details
        }), err.response.status_code
    except Exception as e:
        print(f"💥 Error inesperado en get_customer: {str(e)}")
        return jsonify({"error": "Ocurrió un error interno en el servidor."}), 500

# Pega este nuevo bloque de código al final de tu archivo actions/customer.py

@customer_actions_bp.route('/actions/update_customer', methods=['POST'])
def handle_update_customer():
    """
    Esta función se activa cuando un workflow de GHL ejecuta la acción "Update a Customer".
    """
    ghl_data = request.json
    print(f"📥 Datos recibidos de GHL (update_customer): {json.dumps(ghl_data, indent=2)}")

    smartpasses_api_key = os.environ.get('SMARTPASSES_API_KEY')
    if not smartpasses_api_key:
        print("❌ ERROR: La SMARTPASSES_API_KEY no está configurada.")
        return jsonify({"error": "Configuración del servidor incompleta."}), 500

    # Extraemos los datos obligatorios
    program_id = ghl_data.get('program_id')
    customer_id = ghl_data.get('customer_id')

    if not all([program_id, customer_id]):
        return jsonify({"error": "Program ID y Customer ID son obligatorios."}), 400

    # --- Construir el payload solo con los campos que el usuario proporcionó ---
    # Esto es importante para no borrar datos existentes con valores vacíos.
    payload = {}
    if ghl_data.get('first_name'):
        payload['firstName'] = ghl_data.get('first_name')
    if ghl_data.get('last_name'):
        payload['lastName'] = ghl_data.get('last_name')
    if ghl_data.get('email'):
        payload['email'] = ghl_data.get('email')
    if ghl_data.get('phone'):
        payload['phone'] = ghl_data.get('phone')
    if ghl_data.get('points') is not None: # Usamos 'is not None' para permitir 0 puntos
        payload['points'] = int(ghl_data.get('points'))

    if not payload:
        return jsonify({"error": "Debes proporcionar al menos un campo para actualizar."}), 400

    # Preparar la petición PUT para la API de Smart Passes
    update_customer_url = f"{SMARTPASSES_API_BASE_URL}/programs/{program_id}/customers/{customer_id}"

    headers = {
        "Authorization": smartpasses_api_key,
        "Content-Type": "application/json"
    }

    try:
        print(f"🚀 Enviando payload de actualización a SmartPasses: {json.dumps(payload, indent=2)}")
        response = requests.put(update_customer_url, json=payload, headers=headers)
        response.raise_for_status()

        smartpasses_response = response.json()
        print(f"✅ Cliente actualizado exitosamente: {json.dumps(smartpasses_response, indent=2)}")

        # Devolvemos la respuesta completa a GHL
        return jsonify(smartpasses_response), 200

    except requests.exceptions.HTTPError as err:
        error_details = err.response.text
        print(f"❌ Error HTTP de SmartPasses: {error_details}")
        return jsonify({
            "error": "Fallo en la comunicación con la API de Smart Passes", 
            "details": error_details
        }), err.response.status_code
    except Exception as e:
        print(f"💥 Error inesperado en update_customer: {str(e)}")
        return jsonify({"error": "Ocurrió un error interno en el servidor."}), 500

# Pega este nuevo bloque de código al final de tu archivo actions/customer.py

@customer_actions_bp.route('/actions/delete_customer', methods=['POST'])
def handle_delete_customer():
    """
    Esta función se activa cuando un workflow de GHL ejecuta la acción "Delete a Customer".
    """
    ghl_data = request.json
    print(f"📥 Datos recibidos de GHL (delete_customer): {json.dumps(ghl_data, indent=2)}")

    smartpasses_api_key = os.environ.get('SMARTPASSES_API_KEY')
    if not smartpasses_api_key:
        print("❌ ERROR: La SMARTPASSES_API_KEY no está configurada.")
        return jsonify({"error": "Configuración del servidor incompleta."}), 500

    # Extraemos los datos obligatorios
    program_id = ghl_data.get('program_id')
    customer_id = ghl_data.get('customer_id')

    if not all([program_id, customer_id]):
        return jsonify({"error": "Program ID y Customer ID son obligatorios."}), 400

    # Preparar la petición DELETE para la API de Smart Passes
    delete_customer_url = f"{SMARTPASSES_API_BASE_URL}/programs/{program_id}/customers/{customer_id}"

    headers = {
        "Authorization": smartpasses_api_key
    }

    try:
        print(f"🚀 Solicitando borrado de cliente a SmartPasses...")
        response = requests.delete(delete_customer_url, headers=headers)
        response.raise_for_status()

        print(f"✅ Cliente eliminado exitosamente.")

        # Una petición DELETE exitosa no devuelve contenido, así que enviamos nuestro propio mensaje de éxito.
        return jsonify({"status": "success", "message": "Customer deleted successfully"}), 200

    except requests.exceptions.HTTPError as err:
        error_details = err.response.text
        print(f"❌ Error HTTP de SmartPasses: {error_details}")
        return jsonify({
            "error": "Fallo en la comunicación con la API de Smart Passes", 
            "details": error_details
        }), err.response.status_code
    except Exception as e:
        print(f"💥 Error inesperado en delete_customer: {str(e)}")
        return jsonify({"error": "Ocurrió un error interno en el servidor."}), 500

