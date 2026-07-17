from rest_framework import serializers

from apps.users.validators import UserValidator


class ShareDocumentSerializer(serializers.Serializer):

    # nombre del profesional que recibirá el enlace
    professional_name = serializers.CharField(max_length=255)

    # RUT del profesional, se valida con algoritmo módulo 11
    professional_rut = serializers.CharField(max_length=20)

    # lista de UUIDs de documentos a incluir en el enlace
    document_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
    )

    # horas de validez del enlace (mínimo 1h, máximo 7 días = 168h)
    expires_in_hours = serializers.IntegerField(min_value=1, max_value=168, required=False, default=24)

    def validate_professional_rut(self, value):
        """Valida formato y dígito verificador del RUT usando UserValidator."""
        return UserValidator.validate_rut_format(value)

    def validate_document_ids(self, value):
        # Validación de pertenencia delegada a ShareDocumentService (pendiente JWT).
        # ListField + UUIDField ya garantizan formato válido.
        return value
