import os

from django.utils import timezone
from rest_framework import serializers


class DocumentValidator:

    ALLOWED_EXTENSIONS = [".pdf", ".jpg", ".jpeg", ".png", ".webp"]

    ALLOWED_MIME_TYPES = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/webp",
    ]

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 mb

    MAX_FILE_NAME_LENGTH = 180

    @staticmethod
    def validate_required_file(file):
        # validar archivo obligatorio
        if not file:
            raise serializers.ValidationError("El archivo es obligatorio.")
        return file

    @staticmethod
    def validate_file_extension(file):
        # validar extension de archivo
        _, extension = os.path.splitext(file.name or "")
        extension = extension.lower()

        if extension not in DocumentValidator.ALLOWED_EXTENSIONS:
            raise serializers.ValidationError(
                f"Extension de archivo no permitida. Use: {', '.join(DocumentValidator.ALLOWED_EXTENSIONS)}")
        return file

    @staticmethod
    def validate_file_mime_type(file):
        # validar mime type
        if file.content_type not in DocumentValidator.ALLOWED_MIME_TYPES:
            raise serializers.ValidationError(
                f"Tipo de archivo no permitido. Use: {', '.join(DocumentValidator.ALLOWED_MIME_TYPES)}")
        return file

    @staticmethod
    def validate_file_size(file):
        # validar tamano de archivo
        if file.size > DocumentValidator.MAX_FILE_SIZE:
            raise serializers.ValidationError("El archivo no puede superar los 10 MB.")
        return file

    @staticmethod
    def validate_file_name(file):
        # validar largo de nombre de archivo
        if len(file.name or "") > DocumentValidator.MAX_FILE_NAME_LENGTH:
            raise serializers.ValidationError(f"El nombre del archivo no puede superar los {DocumentValidator.MAX_FILE_NAME_LENGTH} caracteres.")
        return file

    @staticmethod
    def validate_document_file(file):
        # corre todas las validaciones de archivo en orden
        DocumentValidator.validate_required_file(file)
        DocumentValidator.validate_file_extension(file)
        DocumentValidator.validate_file_mime_type(file)
        DocumentValidator.validate_file_size(file)
        DocumentValidator.validate_file_name(file)

        return file

    @staticmethod
    def validate_document_date_not_future(value):
        # validar que la fecha del documento no sea futura
        if value and value > timezone.now().date():
            raise serializers.ValidationError("La fecha del documento no puede ser futura.")
        return value
