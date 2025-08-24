
#!/bin/bash

# Script de inicio para el servidor SmartPasses GHL Bridge

# Cargar variables de entorno si existe el archivo .env
if [ -f .env ]; then
    export $(cat .env | xargs)
fi

# Verificar que las variables críticas estén configuradas
if [ -z "$SMARTPASSES_API_KEY" ]; then
    echo "ERROR: SMARTPASSES_API_KEY no está configurada"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "ERROR: SECRET_KEY no está configurada"
    exit 1
fi

echo "Iniciando servidor SmartPasses GHL Bridge..."

# Crear directorio de logs si no existe
mkdir -p logs

# Iniciar el servidor con Gunicorn
exec gunicorn --bind 0.0.0.0:5000 \
              --workers 2 \
              --timeout 120 \
              --keep-alive 2 \
              --max-requests 1000 \
              --max-requests-jitter 50 \
              --access-logfile logs/access.log \
              --error-logfile logs/error.log \
              --log-level info \
              wsgi:application
