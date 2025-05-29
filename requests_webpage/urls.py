# requests_webpage/urls.py

from django.contrib import admin
from django.urls import path, include # Asegúrate de importar 'include'
from django.conf import settings
from django.conf.urls.static import static
# Importa la vista 'home' si la mantienes aquí (o elimínala si 'portal/dashboard/' es tu nueva home)
from tasks import views as tasks_views # Asume que 'home' está en tasks/views.py

urlpatterns = [
    # URLs del Admin de Django
    path('admin/', admin.site.urls),

    # URLs de Autenticación de Django (login, logout, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # --- Inclusión de las URLs de la app 'tasks' ---
    # Todas las URLs definidas en 'tasks.urls' comenzarán con 'portal/'
    # El 'namespace' permite usar {% url 'tasks:nombre_vista' %} en plantillas
    path('rhino/', include('tasks.urls', namespace='tasks')),
    # --------------------------------------------------

    # URL para la página de inicio principal del sitio (opcional)
    # Si quieres que '/portal/dashboard/' sea la página principal después del login,
    # puedes configurar LOGIN_REDIRECT_URL en settings.py y quitar esta línea,
    # o hacer que esta vista redirija al dashboard si el usuario está autenticado.
    path('', tasks_views.home, name='home'),

    # Nota: Se han movido las URLs como /profile/ y /manage_prices/ a tasks.urls
    #       ya que parecen pertenecer a la funcionalidad de esa aplicación.
]

# --- Configuración para servir archivos Media (SOLO PARA DESARROLLO) ---
# En producción, tu servidor web (Nginx, Apache) debe manejar esto.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)