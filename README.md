
# SmartPasses GHL Bridge Server

Servidor intermediario que conecta GoHighLevel con la API de SmartPasses para gestionar programas de lealtad.

## Funcionalidades

- ✅ Crear clientes en SmartPasses desde GHL
- ✅ Agregar puntos a clientes existentes
- ✅ Obtener información de clientes
- ✅ Actualizar datos de clientes
- ✅ Eliminar clientes
- ✅ Enviar notificaciones push a todos los clientes
- ✅ Manejo de webhooks de GHL con verificación de seguridad
- ✅ Autenticación OAuth con GHL

## Instalación en VPS

### 1. Clonar el repositorio

```bash
git clone <tu-repositorio>
cd smartpasses-ghl-bridge
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
nano .env
```

Configura las siguientes variables:

```env
FLASK_ENV=production
SECRET_KEY=tu-clave-secreta-muy-segura-aqui
SMARTPASSES_API_KEY=tu-api-key-de-smartpasses
GHL_CLIENT_ID=tu-client-id-de-ghl
GHL_CLIENT_SECRET=tu-client-secret-de-ghl
GHL_SHARED_SECRET=tu-shared-secret-para-webhooks
```

### 4. Dar permisos al script de inicio

```bash
chmod +x start.sh
```

### 5. Ejecutar el servidor

```bash
./start.sh
```

## Configuración con Nginx (Recomendado)

Crea un archivo de configuración de Nginx:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Configuración con systemd

Para ejecutar como servicio del sistema, crea `/etc/systemd/system/smartpasses-ghl.service`:

```ini
[Unit]
Description=SmartPasses GHL Bridge Server
After=network.target

[Service]
Type=exec
User=www-data
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/your/app/venv/bin
ExecStart=/path/to/your/app/start.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

Luego ejecuta:

```bash
sudo systemctl enable smartpasses-ghl
sudo systemctl start smartpasses-ghl
```

## Endpoints disponibles

- `GET /` - Página de bienvenida
- `GET /health` - Verificación de salud del servidor
- `POST /actions/create_customer` - Crear cliente en SmartPasses
- `POST /actions/add_points` - Agregar puntos a cliente
- `POST /actions/get_customer` - Obtener información de cliente
- `POST /actions/update_customer` - Actualizar cliente
- `POST /actions/delete_customer` - Eliminar cliente
- `POST /actions/send_push` - Enviar notificación push
- `POST /webhook/ghl` - Recibir webhooks de GHL
- `GET /ghl/oauth/callback` - Callback de OAuth de GHL

## Logs

Los logs se guardan en el directorio `logs/`:
- `access.log` - Logs de acceso
- `error.log` - Logs de errores
- `smartpasses.log` - Logs de la aplicación

## Seguridad

- Todas las peticiones de webhook se verifican con firma HMAC
- Las variables sensibles deben configurarse como variables de entorno
- Se recomienda usar HTTPS en producción
- Los logs no incluyen información sensible
