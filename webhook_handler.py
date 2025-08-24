# webhook_handler.py
# Maneja los webhooks entrantes de GoHighLevel.

from flask import Blueprint, request, jsonify
import hashlib
import hmac
import os
import json

webhook_bp = Blueprint('webhook_handler', __name__)

@webhook_bp.route('/ghl/webhooks', methods=['POST'])
def handle_ghl_webhook():
    """
    Recibe, verifica y procesa las notificaciones de webhook de GHL.
    """
    # --- Verificación de Seguridad (¡Muy Importante!) ---
    # GHL envía una firma en las cabeceras para verificar la autenticidad.
    ghl_signature = request.headers.get('x-webhook-signature')
    shared_secret = os.environ.get('GHL_SHARED_SECRET')

    if not ghl_signature or not shared_secret:
        print("❌ Webhook recibido sin firma o sin Shared Secret configurado.")
        return jsonify({"error": "Configuración de seguridad incompleta."}), 400

    # Calculamos nuestra propia firma usando el cuerpo de la petición y el secreto.
    request_body = request.get_data()
    hashed = hmac.new(shared_secret.encode('utf-8'), request_body, hashlib.sha256)
    calculated_signature = hashed.hexdigest()

    # Comparamos las firmas. Si no coinciden, es una petición falsa.
    if not hmac.compare_digest(calculated_signature, ghl_signature):
        print("❌ ¡Alerta de Seguridad! La firma del webhook es inválida.")
        return jsonify({"error": "Firma inválida."}), 401

    print("✅ Firma del webhook verificada exitosamente.")

    # --- Procesamiento del Webhook ---
    webhook_data = request.json
    event_type = webhook_data.get('type')

    print(f"📥 Webhook recibido de tipo: {event_type}")
    print(f"📋 Datos completos: {json.dumps(webhook_data, indent=2)}")

    if event_type == 'ContactCreate':
        # Aquí iría la lógica para crear automáticamente un cliente en Smart Passes.
        # Por ahora, solo imprimimos un mensaje.
        contact_email = webhook_data.get('email')
        print(f"➡️ Lógica para 'ContactCreate' activada para el email: {contact_email}")
        # Ejemplo: crear_cliente_en_smartpasses(webhook_data)

    elif event_type == 'ContactDelete':
        # Aquí iría la lógica para borrar el cliente en Smart Passes.
        contact_id = webhook_data.get('id')
        print(f"➡️ Lógica para 'ContactDelete' activada para el ID de contacto: {contact_id}")
        # Ejemplo: borrar_cliente_en_smartpasses(contact_id)

    # Le respondemos a GHL con un 200 OK para decirle que recibimos la notificación.
    return jsonify({"status": "success"}), 200
