# actions/program.py
# Contiene la lógica para acciones de GHL relacionadas con programas completos.

from flask import Blueprint, request, jsonify
import requests
import os
import json

program_actions_bp = Blueprint('program_actions', __name__)

SMARTPASSES_API_BASE_URL = "https://pass.smartpasses.io/api/v1/loyalty"

@program_actions_bp.route('/actions/send_push', methods=['POST'])
def handle_send_push():
    """
    Esta función se activa cuando un workflow de GHL ejecuta la acción "Send Push Notification".
    """
    ghl_data = request.json
    print(f"📥 Datos recibidos de GHL (send_push): {json.dumps(ghl_data, indent=2)}")

    smartpasses_api_key = os.environ.get('SMARTPASSES_API_KEY')
    if not smartpasses_api_key:
        print("❌ ERROR: La SMARTPASSES_API_KEY no está configurada.")
        return jsonify({"error": "Configuración del servidor incompleta."}), 500

    program_id = ghl_data.get('program_id')
    message = ghl_data.get('message')

    if not all([program_id, message]):
        return jsonify({"error": "Program ID y Message son obligatorios."}), 400

    # Preparar la petición POST para la API de Smart Passes
    broadcast_url = f"{SMARTPASSES_API_BASE_URL}/programs/{program_id}/broadcast"

    payload = {
        "message": message
    }

    headers = {
        "Authorization": smartpasses_api_key,
        "Content-Type": "application/json"
    }

    try:
        print(f"🚀 Enviando notificación push a SmartPasses...")
        response = requests.post(broadcast_url, json=payload, headers=headers)
        response.raise_for_status()

        # Una petición de broadcast exitosa puede no devolver contenido, así que enviamos nuestro propio mensaje de éxito.
        print(f"✅ Notificación enviada exitosamente.")
        return jsonify({"status": "success", "message": "Push notification sent successfully"}), 200

    except requests.exceptions.HTTPError as err:
        error_details = err.response.text
        print(f"❌ Error HTTP de SmartPasses: {error_details}")
        return jsonify({
            "error": "Fallo en la comunicación con la API de Smart Passes", 
            "details": error_details
        }), err.response.status_code
    except Exception as e:
        print(f"💥 Error inesperado en send_push: {str(e)}")
        return jsonify({"error": "Ocurrió un error interno en el servidor."}), 500
