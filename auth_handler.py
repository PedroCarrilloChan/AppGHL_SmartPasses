# auth_handler.py
# Maneja el flujo de autenticación OAuth 2.0 para GoHighLevel

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

        # --- SECCIÓN MODIFICADA ---
        # Devolvemos una página HTML con el branding de Smart Passes y un botón de acción.
        html_response = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Connection Successful - Smart Passes</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');
                body { 
                    font-family: 'Poppins', sans-serif; 
                    background-color: #0f172a; 
                    color: #e2e8f0;
                    display: flex; 
                    justify-content: center; 
                    align-items: center; 
                    height: 100vh; 
                    margin: 0; 
                    text-align: center; 
                }
                .container { 
                    background-color: #1e293b; 
                    padding: 50px; 
                    border-radius: 12px; 
                    border: 1px solid #334155;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
                    max-width: 500px;
                }
                .brand {
                    font-weight: 600;
                    font-size: 24px;
                    color: #ffffff;
                    margin-bottom: 20px;
                }
                h1 { 
                    color: #10b981; 
                    font-size: 28px;
                    margin-top: 0;
                }
                p { 
                    color: #94a3b8; 
                    font-size: 16px;
                }
                .next-step {
                    border-top: 1px solid #334155;
                    margin-top: 30px;
                    padding-top: 30px;
                }
                .next-step h2 {
                    font-size: 20px;
                    color: #ffffff;
                    margin-top: 0;
                }
                .button {
                    display: inline-block;
                    background-color: #2563eb;
                    color: #ffffff;
                    padding: 12px 24px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: 600;
                    margin-top: 15px;
                    transition: background-color 0.3s;
                }
                .button:hover {
                    background-color: #1d4ed8;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="brand">SmartPasses</div>
                <h1>✓ Connection Successful</h1>
                <p>Your application has been connected successfully.</p>

                <div class="next-step">
                    <h2>Next Steps</h2>
                    <p>To start using the application, you need your credentials (App Key and Program ID). Click the button to request them from our support team.</p>
                    <a href="mailto:support@smartpasses.com?subject=Credential Request for GoHighLevel&body=Hello, I need my API credentials to integrate SmartPasses with GoHighLevel. Please provide me with my App Key and Program ID." class="button">Request Credentials</a>
                </div>
            </div>
        </body>
        </html>
        """
        return html_response

    except Exception as e:
        print(f"Error en el callback de OAuth: {e}")
        # Página de error con el mismo estilo.
        error_html = """
        <!DOCTYPE html>
        <html lang="en"><head><title>Error</title><style>body{font-family:'Poppins',sans-serif;background-color:#0f172a;color:#e2e8f0;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;text-align:center;}.container{background-color:#1e293b;padding:50px;border-radius:12px;border:1px solid #334155;}h1{color:#ef4444;}</style></head>
        <body><div class="container"><h1>✕ Connection Error</h1><p>Authentication could not be completed. Please try again or contact support.</p></div></body></html>
        """
        return error_html, 500