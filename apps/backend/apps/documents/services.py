import os
import uuid

from django.conf import settings
from rest_framework import serializers

from apps.users.services import UserService

from .repositories import DocumentRepository, DocumentCategoryRepository


class DocumentService:

    @staticmethod
    def get_user_by_identifier(email=None, rut=None):
        # validar y buscar usuario por email o rut
        if not email and not rut:
            raise serializers.ValidationError({
                "user": "Debe enviar email o rut como parametro."
            })

        user = UserService.get_user_by_identifier(email=email, rut=rut)

        if not DocumentService.validate_user_exists(user):
            raise serializers.ValidationError({
                "user": "El usuario no existe."
            })

        return user

    @staticmethod
    def get_documents_by_identifier(email=None, rut=None):
        # listar documentos por email o rut
        user = DocumentService.get_user_by_identifier(email=email, rut=rut)

        return DocumentService.get_documents_by_user(user)

    @staticmethod
    def create_document_by_identifier(email=None, rut=None, data=None):
        # crear documento por email o rut
        user = DocumentService.get_user_by_identifier(email=email, rut=rut)

        return DocumentService.create_document(user, data)

    @staticmethod
    def get_document_by_id_and_identifier(document_id, email=None, rut=None):
        # obtener documento por id y email o rut
        user = DocumentService.get_user_by_identifier(email=email, rut=rut)

        return DocumentService.get_document_by_id_and_user(document_id, user)

    @staticmethod
    def delete_document_by_id_and_identifier(document_id, email=None, rut=None):
        # eliminar documento por id y email o rut
        user = DocumentService.get_user_by_identifier(email=email, rut=rut)
        document = DocumentService.get_document_by_id_and_user(document_id, user)

        return DocumentService.delete_document(document)

    @staticmethod
    def get_documents_by_user(user):
        if not DocumentService.validate_user_exists(user):
            raise serializers.ValidationError({
                "user": "El usuario no existe."
            })

        return DocumentRepository.get_all_by_user(user)

    @staticmethod
    def get_document_by_id_and_user(document_id, user):
        if not DocumentService.validate_user_exists(user):
            raise serializers.ValidationError({
                "user": "El usuario no existe."
            })

        document = DocumentRepository.get_by_id_and_user(document_id, user)

        if not DocumentService.validate_document_exists(document):
            raise serializers.ValidationError({
                "document": "El documento no existe o no pertenece al usuario."
            })

        return document

    @staticmethod
    def create_document(user, data):
        if not DocumentService.validate_user_exists(user):
            raise serializers.ValidationError({
                "user": "El usuario no existe."
            })

        # validar archivo obligatorio
        file = data.pop("file", None)

        if not file:
            raise serializers.ValidationError({
                "file": "El archivo es obligatorio."
            })

        # validar categoria obligatoria
        category_id = data.pop("category_id", None)

        if not category_id:
            raise serializers.ValidationError({
                "category_id": "La categoria es obligatoria."
            })

        category = DocumentCategoryRepository.get_by_id(category_id)

        if not DocumentService.validate_category_exists(category):
            raise serializers.ValidationError({
                "category_id": "La categoria indicada no existe."
            })

        # subir archivo a storage antes de guardar en base de datos
        storage_metadata = DocumentStorageService.upload_file(user, category, file)

        data.update(storage_metadata)
        data["category"] = category
        data["user"] = user

        return DocumentRepository.create_document(data)

    # este no sera utilizado hasta la fecha
    @staticmethod
    def update_document(document, data):
        if not DocumentService.validate_document_exists(document):
            raise serializers.ValidationError({
                "document": "El documento no existe."
            })

        category_id = data.pop("category_id", None)

        if category_id:
            category = DocumentCategoryRepository.get_by_id(category_id)

            if not DocumentService.validate_category_exists(category):
                raise serializers.ValidationError({
                    "category_id": "La categoria indicada no existe."
                })

            data["category"] = category

        for field, value in data.items():
            setattr(document, field, value)

        return DocumentRepository.save_document(document)

    @staticmethod
    def delete_document(document):
        if not DocumentService.validate_document_exists(document):
            raise serializers.ValidationError({
                "document": "El documento no existe."
            })

        return DocumentRepository.soft_delete(document)

    @staticmethod
    def validate_user_exists(user):
        return user is not None

    @staticmethod
    def validate_document_exists(document):
        return document is not None

    @staticmethod
    def validate_category_exists(category):
        return category is not None


# mapping de category slug a bucket de supabase storage
CATEGORY_BUCKETS = {
    "recetas-medicas": "documents-recetas-medicas",
    "examenes": "documents-examenes",
    "certificados": "documents-certificados",
}


class DocumentStorageService:

    @staticmethod
    def get_bucket_by_category(category):
        # validar que category exista y tenga slug
        if category is None or not hasattr(category, "slug") or not category.slug:
            raise serializers.ValidationError({
                "category": "La categoria no tiene bucket asociado."
            })

        bucket_name = CATEGORY_BUCKETS.get(category.slug)

        if not bucket_name:
            raise serializers.ValidationError({
                "category": "La categoria no tiene bucket asociado."
            })

        return bucket_name

    @staticmethod
    def get_file_extension(file):
        # obtener extension desde file.name
        _, extension = os.path.splitext(file.name)

        return extension.lower()

    @staticmethod
    def generate_file_key(user, category, file):
        # genera ruta: documents/<user_id>/<category_slug>/<uuid>.<ext>
        extension = DocumentStorageService.get_file_extension(file)
        unique_name = str(uuid.uuid4())

        return f"documents/{user.id}/{category.slug}/{unique_name}{extension}"

    @staticmethod
    def get_file_size_bytes(file):
        # retorna tamano del archivo en bytes
        return file.size

    @staticmethod
    def get_mime_type(file):
        # retorna content type del archivo
        return getattr(file, "content_type", None)

    @staticmethod
    def upload_file(user, category, file):
        # subir archivo a supabase storage y retornar metadata
        supabase_url = getattr(settings, "SUPABASE_URL", "")
        supabase_key = getattr(settings, "SUPABASE_SERVICE_KEY", "")

        if not supabase_url or not supabase_key:
            raise serializers.ValidationError({
                "storage": "Faltan credenciales de supabase storage."
            })

        bucket_name = DocumentStorageService.get_bucket_by_category(category)
        file_key = DocumentStorageService.generate_file_key(user, category, file)
        mime_type = DocumentStorageService.get_mime_type(file)
        file_size_bytes = DocumentStorageService.get_file_size_bytes(file)

        # subir a supabase storage
        try:
            from supabase import create_client

            client = create_client(supabase_url, supabase_key)

            file.seek(0)
            file_bytes = file.read()
            file.seek(0)

            client.storage.from_(bucket_name).upload(
                path=file_key,
                file=file_bytes,
                file_options={"content-type": mime_type} if mime_type else {}
            )
        except serializers.ValidationError:
            raise
        except Exception as error:
            raise serializers.ValidationError({
                "storage": f"Error al subir archivo a storage: {str(error)}"
            })

        return {
            "bucket_name": bucket_name,
            "file_key": file_key,
            "file_url": None,
            "mime_type": mime_type,
            "file_size_bytes": file_size_bytes,
            "extracted_text": "",
        }


class DocumentCategoryService:

    @staticmethod
    def get_categories():
        return DocumentCategoryRepository.get_all()

    @staticmethod
    def get_category_by_id(category_id):
        category = DocumentCategoryRepository.get_by_id(category_id)

        if category is None:
            raise serializers.ValidationError({
                "category_id": "La categoria indicada no existe."
            })

        return category
