from rest_framework import serializers
from .repositories import UserRepository, MedicalProfileRepository


class UserService:
    @staticmethod
    def register_user(data):
        email = data['email']
        rut = data['rut']

        if UserService.validate_email_not_registered(email):
            raise serializers.ValidationError({
                "email": "El email ya esta registrado."
            })

        if UserService.validate_rut_not_registered(rut):
            raise serializers.ValidationError({
                "rut": "usuario ya registrado"
            })

        return UserRepository.create_user(data)

    @staticmethod
    def validate_email_not_registered(email):
        if UserRepository.exists_by_email(email):
            return True

        return False

    @staticmethod
    def validate_rut_not_registered(rut):
        if UserRepository.exists_by_rut(rut):
            return True

        return False

    @staticmethod
    def validate_user_exists(user):
        if user is None:
            return False

        return True

    @staticmethod
    def validate_new_password_is_different(user,new_password):
        return not user.check_password(new_password)

    @staticmethod
    def get_user_by_identifier(email=None, rut=None):
        if email:
            return UserRepository.get_by_email(email)

        if rut:
            return UserRepository.get_by_rut(rut)

        return None

    @staticmethod
    def get_medical_profile(user):
        return MedicalProfileRepository.get_or_create_medical_profile(user)

    @staticmethod
    def update_medical_profile(user, data):
        profile = MedicalProfileRepository.get_or_create_medical_profile(user)

        # Delega la escritura al repositorio para no repetir set/save en la capa service.
        return MedicalProfileRepository.update_fields(profile, data)

    @staticmethod
    def update_profile_image_metadata(user, profile_image_bucket, profile_image_key, profile_image_url=""):
        # Expone la actualizacion de foto para futuros endpoints de subida.
        profile = MedicalProfileRepository.get_or_create_medical_profile(user)

        return MedicalProfileRepository.update_profile_image_metadata(
            profile=profile,
            profile_image_bucket=profile_image_bucket,
            profile_image_key=profile_image_key,
            profile_image_url=profile_image_url,
        )

    @staticmethod
    def clear_profile_image_metadata(user):
        # Permite remover la foto sin borrar el perfil medico.
        profile = MedicalProfileRepository.get_or_create_medical_profile(user)

        return MedicalProfileRepository.clear_profile_image_metadata(profile)

    @staticmethod
    def get_profile_image_metadata(user):
        # Devuelve bucket/key/url sin exponer logica de modelo a la vista.
        profile = MedicalProfileRepository.get_or_create_medical_profile(user)

        return MedicalProfileRepository.get_profile_image_metadata(profile)

    @staticmethod
    def set_current_medications(user, medications):
        profile = MedicalProfileRepository.get_or_create_medical_profile(user)

        return MedicalProfileRepository.set_current_medications(profile, medications)

    @staticmethod
    def set_recent_medical_history(user, history):
        profile = MedicalProfileRepository.get_or_create_medical_profile(user)

        return MedicalProfileRepository.set_recent_medical_history(profile, history)

    @staticmethod
    def set_allergies(user, allergies):
        profile = MedicalProfileRepository.get_or_create_medical_profile(user)

        return MedicalProfileRepository.set_allergies(profile, allergies)

    @staticmethod
    def set_chronic_conditions(user, chronic_conditions):
        profile = MedicalProfileRepository.get_or_create_medical_profile(user)

        return MedicalProfileRepository.set_chronic_conditions(profile, chronic_conditions)

class AuthService:
    @staticmethod
    def login(email, password):
        user = UserRepository.get_by_email(email)

        if not UserService.validate_user_exists(user):
            raise serializers.ValidationError({
                "email": "El usuario no existe."
            })

        if not user.check_password(password):
            raise serializers.ValidationError({
                "password": "La contraseña es incorrecta."
            })

        if not user.is_active:
            raise serializers.ValidationError({
                "user": "El usuario se encuentra desactivado."
            })

        return user

    @staticmethod
    def request_reset(email):
        user = UserRepository.get_by_email(email)

        if not UserService.validate_user_exists(user):
            raise serializers.ValidationError({
                "email": "El usuario no existe"
            })

        return user

    @staticmethod
    def confirm_reset(email, new_password):
        user = UserRepository.get_by_email(email)

        if not UserService.validate_user_exists(user):
            raise serializers.ValidationError({
                "email" : "El usuario no existe"
            })

        if not UserService.validate_new_password_is_different(user,user.password):
            raise serializers.ValidationError({
                "new_password": "La nueva contrasenha no puede ser igual a la anterior."
            })

        user.set_password(new_password)

        return UserRepository.save_user(user)
