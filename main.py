
# main.py
# Archivo de compatibilidad para desarrollo local

from app import create_app
import os

# Crear la aplicacióncdfdf
app = create_app()

# --- Ejecutar el servidor ---
if __name__ == '__main__':
    # Para desarrollo local
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 81)), debug=True)
