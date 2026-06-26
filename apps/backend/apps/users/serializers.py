import re
from datetime import date
from urllib.parse import urlparse
from rest_framework import serializers
from .models import MedicalProfile
from .validators import UserValidator


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, min_length=10, max_length=60)
    email = serializers.EmailField(required=True)
    rut = serializers.CharField(required=True, min_length=8, max_length=12)
    password = serializers.CharField(required=True, min_length=6, max_length=12, write_only=True)

    # la base que se usara, aqui crearemos las validaciones de entrada
    def validate_email(self, value):
        return UserValidator.validate_email_format(value)

    def validate_rut(self, value):
        return UserValidator().validate_rut_format(value)

    def validate_password(self, value):
        return UserValidator().validate_password_strength(value)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate_email(self, value):
        return UserValidator.validate_email_format(value)

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        return UserValidator.validate_email_format(value)

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    new_password = serializers.CharField(required=True, min_length=6, max_length=12, write_only=True)
    confirm_password = serializers.CharField(required=True, min_length=6, max_length=12, write_only=True)

    def validate_email(self, value):
        return UserValidator.validate_email_format(value)

    def validate_new_password(self, value):
        return UserValidator.validate_password_strength(value)

    def validate_confirm_password(self, value):
        return UserValidator.validate_password_strength(value)

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        if new_password != confirm_password:
            raise serializers.ValidationError({
                "confirm_password": "Las contraseñas no coinciden."
            })

        return attrs

class UserSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    email = serializers.EmailField()
    rut = serializers.CharField()
    name = serializers.CharField()


# Serializa un medicamento del campo JSON current_medications
class MedicationSerializer(serializers.Serializer):
    id = serializers.UUIDField(required=False)
    name = serializers.CharField(max_length=100)
    dose = serializers.CharField(max_length=50, required=False, allow_blank=True)
    frequency = serializers.CharField(max_length=100, required=False, allow_blank=True)
    start_date = serializers.DateField(required=False, allow_null=True)
    end_date = serializers.DateField(required=False, allow_null=True)
    notes = serializers.CharField(max_length=255, required=False, allow_blank=True)
    active = serializers.BooleanField(default=True)

    # Valida que end_date no sea anterior a start_date
    def validate(self, attrs):
        start = attrs.get("start_date")
        end = attrs.get("end_date")
        if start and end and end < start:
            raise serializers.ValidationError(
                {"end_date": "La fecha de fin no puede ser anterior a la fecha de inicio."}
            )
        return attrs


# Serializa la subida de imagen de perfil del paciente
class ProfileImageUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

    # MIME types permitidos para imagen de perfil
    ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
    MAX_SIZE = 5 * 1024 * 1024  # 5 MB

    def validate_file(self, file):
        if file.content_type not in self.ALLOWED_TYPES:
            raise serializers.ValidationError(
                f"Tipo de archivo no permitido. Use: {', '.join(self.ALLOWED_TYPES)}"
            )
        if file.size > self.MAX_SIZE:
            raise serializers.ValidationError(
                "El archivo no puede superar los 5 MB."
            )
        return file


class MedicalProfileSerializer(serializers.ModelSerializer):
    # Email del usuario dueño del perfil, solo lectura via relacion User
    email = serializers.EmailField(source="user.email", read_only=True)
    imc = serializers.SerializerMethodField()

    class Meta:
        model = MedicalProfile
        fields = [
            "email",
            "first_name",
            "last_name",
            "birthdate",
            "genre",
            "blood_type",
            "weight",
            "height",
            "profile_image_url",
            "phone_number",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_email",
            "emergency_contact_relationship",
            "relevant_clinical_information",
            "imc",
            "updated_at",
            "address",
            "profile_image_bucket",
            "profile_image_key",
            "relevance_type",
            "current_medications",
            "recent_medical_history",
            "allergies",
            "chronic_conditions",
        ]
        read_only_fields = [
            "email",
            "updated_at",
            "imc",
            "profile_image_url",
            "profile_image_bucket",
            "profile_image_key",
        ]
    #Integracion validadores campos de perfil medico.
    def validate_first_name(self, value):
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$', value):
            raise serializers.ValidationError("El nombre solo puede contener letras y espacios.")
        if len(value) < 2:
            raise serializers.ValidationError("El nombre debe tener al menos 2 caracteres.")
        if len(value) > 48:
            raise serializers.ValidationError("El nombre no puede tener más de 48 caracteres.")
        return value.strip()

    def validate_last_name(self, value):
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$', value):
            raise serializers.ValidationError("El apellido solo puede contener letras y espacios.")
        if len(value) < 2:
            raise serializers.ValidationError("El apellido debe tener al menos 2 caracteres.")
        if len(value) > 48:
            raise serializers.ValidationError("El apellido no puede tener más de 48 caracteres.")
        return value.strip()

    def validate_birthdate(self, value):
        if value is None:
            return value
        today = date.today()
        if value > today:
            raise serializers.ValidationError("La fecha de nacimiento no puede ser futura.")
        age = (today - value).days // 365
        if age > 120:
            raise serializers.ValidationError("La fecha de nacimiento no es válida (edad máxima 120 años).")
        return value

    def validate_genre(self, value):
        valid_genres = ["Masculino", "Femenino", "No binario", "Otro"]
        if value and value not in valid_genres:
            raise serializers.ValidationError(f"Género no válido. Opciones: {', '.join(valid_genres)}.")
        return value

    def validate_blood_type(self, value):
        valid_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        if value and value not in valid_types:
            raise serializers.ValidationError(f"Tipo de sangre no válido. Opciones: {', '.join(valid_types)}.")
        return value

    def validate_profile_image_url(self, value):
        if not value:
            return value
        try:
            result = urlparse(value)
            if not all([result.scheme, result.netloc]):
                raise serializers.ValidationError("URL de imagen no válida.")
            if result.scheme != "https":
                raise serializers.ValidationError("La imagen debe ser una URL HTTPS.")
        except Exception:
            raise serializers.ValidationError("URL de imagen no válida.")
        return value

    def validate_weight(self, value):
        if value is not None:
            if value <= 0:
                raise serializers.ValidationError("El peso debe ser mayor a 0.")
            if value > 500:
                raise serializers.ValidationError("El peso no puede ser mayor a 500 kg.")
        return value

    def validate_height(self, value):
        if value is not None:
            if value <= 0:
                raise serializers.ValidationError("La altura debe ser mayor a 0.")
            if value > 250:
                raise serializers.ValidationError("La altura no puede ser mayor a 250 cm.")
        return value

    # Valida formato de telefono: numeros, +, espacios, largo 8-20
    def validate_phone_number(self, value):
        return UserValidator.validate_phone_format(value, "phone_number")

    def validate_emergency_contact_phone(self, value):
        return UserValidator.validate_phone_format(value, "emergency_contact_phone")

    # Valida cada medicamento del array usando MedicationSerializer
    def validate_current_medications(self, value):
        if value is None:
            return value
        if not isinstance(value, list):
            raise serializers.ValidationError("El campo 'current_medications' debe ser un array JSON.")
        serializer = MedicationSerializer(data=value, many=True)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    # Valida historial medico reciente: title requerido, type y description opcionales
    def validate_recent_medical_history(self, value):
        schema = {
            "title":       {"required": True, "max_length": 100},
            "type":        {"max_length": 50},
            "description": {"max_length": 500},
        }
        return UserValidator.validate_json_list_of_dicts(value, "recent_medical_history", schema)

    # Lista de strings, cada uno max 50 caracteres
    def validate_relevance_type(self, value):
        return UserValidator.validate_json_list_of_strings(value, "relevance_type", max_length=50)

    # Lista de strings, cada uno max 100 caracteres
    def validate_allergies(self, value):
        return UserValidator.validate_json_list_of_strings(value, "allergies", max_length=100)

    # Lista de strings, cada uno max 100 caracteres
    def validate_chronic_conditions(self, value):
        return UserValidator.validate_json_list_of_strings(value, "chronic_conditions", max_length=100)

    def get_imc(self, obj):
        if obj.weight and obj.height:
            height_m = obj.height / 100
            imc = obj.weight / (height_m ** 2)
            return round(imc, 1)
        return None
