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

@customer_actions_bp.route('/actions/create_customer', methods=['POST'])
def handle_create_customer():
    ghl_data = request.json
    print(f"📥 Datos recibidos de GHL (create_customer): {json.dumps(ghl_data, indent=2)}")

    # --- CAMBIO CLAVE: Obtener credenciales dinámicamente ---
    location_id = ghl_data.get('locationId') # GHL envía el ID de la sub-cuenta
    if not location_id:
        return jsonify({"error": "No se recibió el Location ID de la sub-cuenta."}), 400

    # Buscamos las credenciales que la agencia guardó en la página de configuración
    agency_credentials = credentials_db.get(location_id)
    if not agency_credentials:
        return jsonify({"error": "La aplicación no ha sido configurada. Por favor, guarde sus credenciales en la página de configuración de la app."}), 400

    smartpasses_api_key = agency_credentials.get('smartpasses_api_key')
    # Usamos el Program ID que el usuario pone en el workflow, o el que guardó por defecto
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
        # (Aquí va el resto de tu lógica para procesar la respuesta...)
        return jsonify(smartpasses_response), 200
    except requests.exceptions.HTTPError as err:
        return jsonify({
            "error": "Fallo en la comunicación con la API de Smart Passes", 
            "details": err.response.text
        }), err.response.status_code
    except Exception as e:
        return jsonify({"error": "Ocurrió un error interno en el servidor."}), 500

# ... (El resto de tus funciones de acciones de cliente irían aquí, siguiendo el mismo patrón de búsqueda de credenciales)
