
# webhook_handler.py
# Maneja las notificaciones de webhook que llegan de GoHighLevel.

from flask import Blueprint, request, jsonify
import hmac
import hashlib
import json
import os

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/webhook/ghl', methods=['POST'])
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

    # Aquí puedes agregar lógica específica según el tipo de evento
    # Por ejemplo:
    # if event_type == 'contact.created':
    #     handle_contact_created(webhook_data)
    # elif event_type == 'contact.updated':
    #     handle_contact_updated(webhook_data)

    # Por ahora, solo confirmamos que recibimos el webhook
    return jsonify({"status": "received", "type": event_type}), 200

def handle_contact_created(data):
    """Maneja cuando se crea un nuevo contacto en GHL"""
    print(f"🆕 Nuevo contacto creado: {data.get('contact', {}).get('email')}")
    # Aquí puedes agregar lógica para crear automáticamente el cliente en SmartPasses

def handle_contact_updated(data):
    """Maneja cuando se actualiza un contacto en GHL"""
    print(f"🔄 Contacto actualizado: {data.get('contact', {}).get('email')}")
    # Aquí puedes agregar lógica para actualizar el cliente en SmartPasses
