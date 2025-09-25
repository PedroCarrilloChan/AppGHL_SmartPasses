# En el archivo: settings_handler.py

@settings_bp.route('/settings/save', methods=['POST'])
def save_settings():
    data = request.get_json()
    location_id = data.get('locationId')
    api_key = data.get('apiKey')
    program_id = data.get('programId')

    # --- INICIO DE LA MEJORA ---
    # Verificación explícita para asegurarnos de que el location_id no sea nulo
    if not location_id or location_id == 'None':
        print(f"🚨 ERROR CRÍTICO: Se intentó guardar credenciales sin un Location ID válido.")
        return jsonify({"error": "Location ID is missing. The app might not be configured correctly in the GHL Marketplace."}), 400
    # --- FIN DE LA MEJORA ---

    if not all([api_key, program_id]):
        return jsonify({"error": "Faltan campos obligatorios (API Key o Program ID)."}), 400

    sql = "INSERT OR REPLACE INTO sub_account_credentials (location_id, api_key, program_id) VALUES (?, ?, ?);"
    params = [location_id, api_key, program_id]

    result, error = query_d1(sql, params)

    if error:
        print(f"🚨 ERROR al guardar en D1: {error[0]}")
        return jsonify({"error": "No se pudieron guardar las credenciales en la base de datos."}), error[1]

    print(f"✅ Credenciales guardadas en Cloudflare D1 para Location ID: {location_id}")
    return jsonify({"status": "success", "message": "Configuración guardada exitosamente."}), 200