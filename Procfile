release: python manage.py migrate
web: gunicorn requests_webpage.wsgi --log-file -
worker: python manage.py qcluster