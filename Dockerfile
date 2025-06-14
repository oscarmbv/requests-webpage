ARG PYTHON_VERSION=3.12.10
FROM python:${PYTHON_VERSION}-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Añadimos netcat-openbsd para el script de espera y otras dependencias
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev netcat-openbsd && rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY requirements.txt /code/
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code/

# Copiamos nuestro script de entrada y lo hacemos ejecutable DENTRO del contenedor
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# Definimos que nuestro script es el punto de entrada
ENTRYPOINT ["/entrypoint.sh"]
# El comando por defecto que recibirá el entrypoint (lo definiremos mejor en fly.toml)
CMD ["gunicorn", "requests_webpage.wsgi"]