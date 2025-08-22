# main.py
# Servidor intermediario para conectar GoHighLevel con la API de Smart Passes.

from flask import Flask, request, jsonify
import requests
import os

# --- Configuración Inicial ---
# Inicializa la aplicación del servidor.
app = Flask(__name__)

# La URL base de tu API de Smart Passes.
SMARTPASSES_API_BASE_URL = "https://pass.smartpasses.io/api/v1/loyalty"

# --- Endpoint para la Acción "Crear Cliente" de GHL ---
# Esta es la URL que debes pegar en la configuración de tu acción en GoHighLevel.
@app.route('/actions/create_customer', methods=['POST'])
def handle_create_customer():
    """
    Esta función se activa cuando un workflow de GHL ejecuta la acción "Create Smart Passes Customer".
    """
    # 1. Recibir los datos que envía GoHighLevel.
    ghl_data = request.json
    print(f"Datos recibidos de GHL: {ghl_data}")

    # Extraemos los datos usando las "Reference keys" que definimos en GHL.
    # En una aplicación real, aquí buscarías en tu base de datos la API Key de la agencia que hizo la petición.
    # Por ahora, la tomaremos de los "Secrets" de Replit.
    smartpasses_api_key = os.environ.get('SMARTPASSES_API_KEY')
    if not smartpasses_api_key:
        print("ERROR: La SMARTPASSES_API_KEY no está configurada en los Secrets de Replit.")
        return jsonify({"error": "Configuración del servidor incompleta."}), 500

    program_id = ghl_data.get('program_id')
    first_name = ghl_data.get('contact_first_name')
    last_name = ghl_data.get('contact_last_name')
    email = ghl_data.get('contact_email')
    phone = ghl_data.get('contact_phone')

    # Validación básica para asegurar que tenemos los datos mínimos.
    if not program_id or not email:
        return jsonify({"error": "El Program ID y el Email son obligatorios."}), 400

    # 2. Preparar la petición para la API de Smart Passes.
    smartpasses_url = f"{SMARTPASSES_API_BASE_URL}/programs/{program_id}/customers"

    smartpasses_payload = {
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "phone": phone
    }

    headers = {
        "Authorization": smartpasses_api_key,
        "Content-Type": "application/json"
    }

    # 3. Llamar a la API de Smart Passes.
    try:
        print(f"Enviando petición a Smart Passes: {smartpasses_url}")
        response = requests.post(smartpasses_url, json=smartpasses_payload, headers=headers)
        response.raise_for_status()  # Esto genera un error si la respuesta es 4xx o 5xx.

        # 4. Procesar la respuesta y devolverla a GoHighLevel.
        response_data = response.json()
        print(f"Cliente creado exitosamente en Smart Passes: {response_data}")

        # Devolvemos el nuevo ID del cliente. GHL podrá usar esto en "Custom Variables".
        return jsonify({
            "new_customer_id": response_data.get("id"),
            "status": "success"
        }), 200

    except requests.exceptions.HTTPError as err:
        # Si la API de Smart Passes devuelve un error, se lo pasamos a GHL.
        print(f"Error de la API de Smart Passes: {err.response.text}")
        return jsonify({"error": "Fallo al crear el cliente en Smart Passes", "details": err.response.text}), err.response.status_code
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return jsonify({"error": "Ocurrió un error interno en el servidor."}), 500

# --- Endpoint de bienvenida para probar que el servidor está funcionando ---
@app.route('/')
def index():
    return "El servidor intermediario de Smart Passes para GHL está funcionando."

# --- Ejecutar el servidor ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

