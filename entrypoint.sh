#!/bin/bash
# entrypoint.sh

# Salir inmediatamente si un comando falla.
set -e

# El host de la base de datos es el nombre de la app de postgres seguido de .internal.
# Fly.io lo resuelve a través de su DNS interno.
DB_HOST="rhino-requests-portal-db.internal"
DB_PORT="5432"

echo "Entrypoint: Esperando a que la base de datos en $DB_HOST:$DB_PORT esté disponible..."

# Usamos nc (netcat) para esperar a que el puerto de la base de datos esté abierto.
# El bucle intentará conectar cada segundo hasta que lo logre.
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  echo "Entrypoint: La base de datos aún no está lista. Reintentando en 1 segundo..."
  sleep 1
done

echo "Entrypoint: ¡La base de datos está disponible! Continuando con el comando..."

# Esta línea ejecuta el comando que se le pasó como argumento a este script
# (por ejemplo, "gunicorn requests_webpage.wsgi" o "python manage.py migrate").
exec "$@"