# auth_handler.py
# Maneja el flujo de autenticación OAuth 2.0 para GoHighLevel.

from flask import Blueprint, request
import requests
import os

auth_bp = Blueprint('auth', __name__)

GHL_OAUTH_TOKEN_URL = "https://api.msgsndr.com/oauth/token"

@auth_bp.route('/oauth/callback')
def ghl_oauth_callback():
    auth_code = request.args.get('code')
    if not auth_code:
        return "Error: No se recibió el código de autorización de GoHighLevel.", 400

    print(f"Código de autorización recibido: {auth_code}")

    payload = {
        'client_id': os.environ.get('GHL_CLIENT_ID'),
        'client_secret': os.environ.get('GHL_CLIENT_SECRET'),
        'grant_type': 'authorization_code',
        'code': auth_code,
        'user_type': 'Location'
    }
    try:
        response = requests.post(GHL_OAUTH_TOKEN_URL, data=payload)
        response.raise_for_status()
        token_data = response.json()

        print("--- ¡AUTENTICACIÓN EXITOSA! ---")
        print(f"Token Data: {token_data}")
        print("---------------------------------")

        # En una app real, aquí guardarías los tokens en tu base de datos.
        # guardar_credenciales_en_db(token_data.get('locationId'), token_data.get('access_token'), token_data.get('refresh_token'))

        return "¡Felicidades! Tu aplicación ha sido conectada exitosamente. Puedes cerrar esta ventana."
    except Exception as e:
        print(f"Error en el callback de OAuth: {e}")
        return "Error al conectar la aplicación.", 500
