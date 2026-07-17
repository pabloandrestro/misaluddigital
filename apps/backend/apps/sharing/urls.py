from django.urls import path
from . import views

# rutas para compartir documentos mediante enlaces temporales
urlpatterns = [
    # crear enlace compartido
    path("", views.create_share_link, name="sharing-create"),

    # abrir enlace compartido mediante token
    path("<str:token>/", views.get_share_link, name="sharing-get"),
]
