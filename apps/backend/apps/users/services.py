from rest_framework import serializers
from .repositories import UserRepository, MedicalProfileRepository
from pathlib import Path
from uuid import uuid4
from django.conf import settings
from supabase import create_client

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
                "rut": "El rut ya esta registrado."
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
    def validate_identifier_provided(email=None, rut=None):
        # exige que venga al menos un identificador
        if not email and not rut:
            raise serializers.ValidationError({
                "identifier": "se requiere email o rut."
            })

    @staticmethod
    def validate_user_instance(user):
        # evita continuar con un user nulo
        if user is None:
            raise serializers.ValidationError({
                "user": "usuario no valido."
            })

    @staticmethod
    def validate_profile_data(data):
        # exige un dict para poder actualizar el perfil
        if data is None or not isinstance(data, dict):
            raise serializers.ValidationError({
                "data": "datos de perfil invalidos."
            })

    @staticmethod
    def validate_list_payload(value, field_name):
        # exige que el payload sea una lista
        if not isinstance(value, list):
            raise serializers.ValidationError({
                field_name: "debe ser una lista."
            })

    @staticmethod
    def validate_text_payload(value, field_name):
        # exige que el payload sea texto
        if not isinstance(value, str):
            raise serializers.ValidationError({
                field_name: "debe ser texto."
            })

    @staticmethod
    def get_user_by_identifier(email=None, rut=None):
        UserService.validate_identifier_provided(email=email, rut=rut)

        if email:
            user = UserRepository.get_by_email(email)

            if user:
                return user

        if rut:
            return UserRepository.get_by_rut(rut)

        return None

    @staticmethod
    def get_medical_profile(user):
        UserService.validate_user_instance(user)

        return MedicalProfileRepository.get_or_create_medical_profile(user)

    @staticmethod
    def update_medical_profile(user, data):
        UserService.validate_user_instance(user)
        UserService.validate_profile_data(data)

        profile = MedicalProfileRepository.get_or_create_medical_profile(user)

        # si no hay datos, devuelve el perfil actual sin romper
        if not data:
            return profile

        # delega la escritura al repositorio para no repetir set/save en la capa service.
        return MedicalProfileRepository.update_fields(profile, data)

    @staticmethod
    def update_profile_image_metadata(user, profile_image_bucket, profile_image_key, profile_image_url=""):
        UserService.validate_user_instance(user)
        UserService.validate_text_payload(profile_image_bucket, "profile_image_bucket")
        UserService.validate_text_payload(profile_image_key, "profile_image_key")

        # url es opcional pero si viene debe ser texto
        if profile_image_url is not None:
            UserService.validate_text_payload(profile_image_url, "profile_image_url")

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
        UserService.validate_user_instance(user)

        # Permite remover la foto sin borrar el perfil medico.
        profile = MedicalProfileRepository.get_or_create_medical_profile(user)

        return MedicalProfileRepository.clear_profile_image_metadata(profile)

    @staticmethod
    def get_profile_image_metadata(user):
        UserService.validate_user_instance(user)

        # Devuelve bucket/key/url sin exponer logica de modelo a la vista.
        profile = MedicalProfileRepository.get_or_create_medical_profile(user)

        return MedicalProfileRepository.get_profile_image_metadata(profile)

    @staticmethod
    def set_current_medications(user, medications):
        UserService.validate_user_instance(user)
        UserService.validate_list_payload(medications, "current_medications")

        profile = MedicalProfileRepository.get_or_create_medical_profile(user)

        return MedicalProfileRepository.set_current_medications(profile, medications)

    @staticmethod
    def set_recent_medical_history(user, history):
        UserService.validate_user_instance(user)
        UserService.validate_list_payload(history, "recent_medical_history")

        profile = MedicalProfileRepository.get_or_create_medical_profile(user)

        return MedicalProfileRepository.set_recent_medical_history(profile, history)

    @staticmethod
    def set_allergies(user, allergies):
        UserService.validate_user_instance(user)
        UserService.validate_list_payload(allergies, "allergies")

        profile = MedicalProfileRepository.get_or_create_medical_profile(user)

        return MedicalProfileRepository.set_allergies(profile, allergies)

    @staticmethod
    def set_chronic_conditions(user, chronic_conditions):
        UserService.validate_user_instance(user)
        UserService.validate_list_payload(chronic_conditions, "chronic_conditions")

        profile = MedicalProfileRepository.get_or_create_medical_profile(user)

        return MedicalProfileRepository.set_chronic_conditions(profile, chronic_conditions)

    # para subir la imagen
    @staticmethod
    def upload_user_profile_image(user, file):
        UserService.validate_user_instance(user)

        if not file:
            raise serializers.ValidationError({
                "image" : "Debe de adjuntar una imagen."
            })

        current_metada = UserService.get_profile_image_metadata(user)

        old_key = current_metada.get("profile_image_key")

        image_data = ProfileStorageService.upload_profile_image(user, file)
        try:
            profile = UserService.update_profile_image_metadata(
                user=user,
                profile_image_bucket=image_data["profile_image_bucket"],
                profile_image_key=image_data["profile_image_key"],
                profile_image_url=image_data["profile_image_url"],
            )

        except Exception:
            ProfileStorageService.delete_profile_image(
                image_data["profile_image_key"]
            )
            raise
        if old_key and old_key != image_data["profile_image_key"]:
            try:
                ProfileStorageService.delete_profile_image(old_key)
            except Exception:
                pass

        return profile

    # para eliminar la foto
    @staticmethod
    def delete_user_profile_image(user):
        UserService.validate_user_instance(user)

        current_metadata = UserService.get_profile_image_metadata(user)
        current_key = current_metadata.get("profile_image_key")

        if current_key:
            ProfileStorageService.delete_profile_image(current_key)

        return UserService.clear_profile_image_metadata(user)

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

        if not UserService.validate_new_password_is_different(user, new_password):
            raise serializers.ValidationError({
                "new_password": "La nueva contrasenha no puede ser igual a la anterior."
            })

        user.set_password(new_password)
        UserRepository.save_user(user)

        return True

# dedicado al storage de profile / medical profile
class ProfileStorageService:
    PROFILE_IMAGE_BUCKET = getattr(settings, "SUPABASE_PROFILE_IMAGE_BUCKET", "profile-images") # nombre del bucket de imagenes

    @staticmethod
    def get_supabase_client():
        # url del supa y su key
        supabase_url = getattr(settings, "SUPABASE_URL", None)
        supabase_key = getattr(settings, "SUPABASE_SERVICE_KEY", None)

        # si vienen vacias o nulas
        if not supabase_url or not supabase_key:
            raise serializers.ValidationError({
                "storage" : "Faltan creedenciales de Supabase Storage."
            })

        return create_client(supabase_url, supabase_key)

    # esta funcion genera la key para la subida
    @staticmethod
    def build_profile_image_key(user, file):
        extension = Path(file.name).suffix.lower()
        return f"{user.id}/{uuid4().hex}{extension}"

    @staticmethod
    def upload_profile_image(user, file):
        # se valida el user
        UserService.validate_user_instance(user)

        # se valida que no venga null o blank
        if not file:
            raise serializers.ValidationError({
                "image" : "Debe de adjuntar una imagen de perfil"
            })

        # se crea el cliente
        supabase = ProfileStorageService.get_supabase_client()

        # define el bucket
        bucket = ProfileStorageService.PROFILE_IMAGE_BUCKET

        # genera la key unica
        key = ProfileStorageService.build_profile_image_key(user, file)

        # cuando se hace read solo es como leerlo desde el incio al final, y devuelve un vacio
        # por lo que el seek 0 mueve el puntero al inicio, lo lee, y lo vuelve a dejar al inicio.
        # asi evitamos que deje un return NULL / Blank
        file.seek(0)
        file_content = file.read()
        file.seek(0)

        # lo sube al bucket
        supabase.storage.from_(bucket).upload(
            key,
            file_content,
            {"content-type": file.content_type,
            "upsert": "true",},)

        # obtiene la public url
        public_url = supabase.storage.from_(bucket).get_public_url(key)

        # retorna la metada para la bd
        return {
            "profile_image_bucket": bucket,
            "profile_image_key": key,
            "profile_image_url": public_url,
        }

     # Para eliminar la imagen del perfil
    @staticmethod
    def delete_profile_image(profile_image_key):
        if not profile_image_key:
            return False

        supabase = ProfileStorageService.get_supabase_client()

        supabase.storage.from_(
            ProfileStorageService.PROFILE_IMAGE_BUCKET
        ).remove([profile_image_key])

        return True