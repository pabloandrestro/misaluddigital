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

class MedicalProfileSerializer(serializers.ModelSerializer):
    imc = serializers.SerializerMethodField()

    class Meta:
        model = MedicalProfile
        fields = [
            "first_name",
            "last_name",
            "birthdate",
            "genre",
            "blood_type",
            "weight",
            "height",
            "profile_image",
            "allergies",
            "chronic_conditions",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relationship",
            "imc",
            "updated_at",
            "address",
            "relevance_type",
            "current_medications",
            "recent_medical_history",
        ]
        read_only_fields = [
            "updated_at",
            "imc",
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

    def validate_profile_image(self, value):
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

    def validate_emergency_contact_phone(self, value):
        if not value:
            return value
        clean_value = value.replace("-", "").replace(" ", "")
        pattern = r'^(\+56)?9\d{8}$'
        if not re.match(pattern, clean_value):
            raise serializers.ValidationError("Formato de teléfono no válido. Ejemplo: +56912345678 o 912345678")
        return value

    def get_imc(self, obj):
        if obj.weight and obj.height:
            height_m = obj.height / 100
            imc = obj.weight / (height_m ** 2)
            return round(imc, 1)
        return None
