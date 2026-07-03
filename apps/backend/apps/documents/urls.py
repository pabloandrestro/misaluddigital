from django.urls import path

from .views import (
    documents_view,
    document_detail_view,
    document_categories_view,
)

urlpatterns = [
    # lista categorias para clasificar documentos
    path("categories/", document_categories_view, name="document_categories"),

    # lista documentos y permite crear/subir nuevos documentos
    path("", documents_view, name="documents"),

    # maneja detalle, actualizacion y eliminacion por documento
    path("<uuid:document_id>/", document_detail_view, name="document_detail"),
]
