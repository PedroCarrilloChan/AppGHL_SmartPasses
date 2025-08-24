
import os
from app import create_app

# Crear la aplicación usando la configuración de producción
application = create_app('production')

if __name__ == "__main__":
    application.run()
