from django.contrib.auth import get_user_model

from .models import MedicalProfile

User = get_user_model()


class UserRepository:
    @staticmethod
    def get_by_id(user_id):
        return User.objects.filter(
            id=user_id
        ).first()

    @staticmethod
    def get_by_email(email):
        return User.objects.filter(
            email=email
        ).first()

    @staticmethod
    def get_by_rut(rut):
        return User.objects.filter(
            rut=rut
        ).first()

    @staticmethod
    def exists_by_email(email):
        return User.objects.filter(
            email=email
        ).exists()

    @staticmethod
    def exists_by_rut(rut):
        return User.objects.filter(
            rut=rut
        ).exists()

    @staticmethod
    def create_user(data):
        user = User.objects.create_user(
            email=data["email"],
            password=data["password"],
            rut=data["rut"],
            name=data["name"]
        )

        return user

    @staticmethod
    def save_user(user):
        user.save()

        return user

class MedicalProfileRepository:
    @staticmethod
    def get_by_user(user):
        return MedicalProfile.objects.filter(
            user=user
        ).first()

    @staticmethod
    def get_or_create_medical_profile(user):
        profile, created = MedicalProfile.objects.get_or_create(
            user=user,
            defaults={
                "first_name": "",
                "last_name": "",
            }
        )

        return profile

    @staticmethod
    def save_medical_profile(profile):
        profile.save()

        return profile

    @staticmethod
    def get_or_create_by_user(user):
        return MedicalProfileRepository.get_or_create_medical_profile(user)

    @staticmethod
    def save(profile):
        return MedicalProfileRepository.save_medical_profile(profile)

    @staticmethod
    def update_fields(profile, data):
        updated_fields = []

        for field, value in data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
                updated_fields.append(field)

        if updated_fields:
            profile.save(update_fields=updated_fields)

        return profile

    @staticmethod
    def update_profile_image_metadata(profile, profile_image_bucket, profile_image_key, profile_image_url=""):
        # Guarda la referencia del archivo subido sin almacenar la imagen en PostgreSQL.
        profile.profile_image_bucket = profile_image_bucket or ""
        profile.profile_image_key = profile_image_key or ""
        profile.profile_image_url = profile_image_url or ""
        profile.profile_image = profile_image_url or ""
        profile.save(update_fields=[
            "profile_image_bucket",
            "profile_image_key",
            "profile_image_url",
            "profile_image",
            "updated_at",
        ])

        return profile

    @staticmethod
    def clear_profile_image_metadata(profile):
        # Limpia la foto cuando el usuario elimina o reemplaza su imagen.
        profile.profile_image_bucket = ""
        profile.profile_image_key = ""
        profile.profile_image_url = ""
        profile.profile_image = ""
        profile.save(update_fields=[
            "profile_image_bucket",
            "profile_image_key",
            "profile_image_url",
            "profile_image",
            "updated_at",
        ])

        return profile

    @staticmethod
    def get_profile_image_metadata(profile):
        # Centraliza la lectura de metadata para respuestas y servicios.
        return {
            "profile_image_bucket": profile.profile_image_bucket,
            "profile_image_key": profile.profile_image_key,
            "profile_image_url": profile.profile_image_url,
            "profile_image": profile.profile_image,
        }

    @staticmethod
    def get_json_field(profile, field_name):
        # Evita repetir lecturas defensivas en campos JSON del perfil.
        if not hasattr(profile, field_name):
            return []

        value = getattr(profile, field_name)
        return value if value is not None else []

    @staticmethod
    def set_json_field(profile, field_name, value):
        # Actualiza campos JSON reutilizables manteniendo listas vacias por defecto.
        if not hasattr(profile, field_name):
            return profile

        setattr(profile, field_name, value or [])
        profile.save(update_fields=[field_name, "updated_at"])

        return profile

    @staticmethod
    def get_current_medications(profile):
        return MedicalProfileRepository.get_json_field(profile, "current_medications")

    @staticmethod
    def set_current_medications(profile, medications):
        return MedicalProfileRepository.set_json_field(
            profile,
            "current_medications",
            medications,
        )

    @staticmethod
    def get_recent_medical_history(profile):
        return MedicalProfileRepository.get_json_field(profile, "recent_medical_history")

    @staticmethod
    def set_recent_medical_history(profile, history):
        return MedicalProfileRepository.set_json_field(
            profile,
            "recent_medical_history",
            history,
        )

    @staticmethod
    def get_allergies(profile):
        return MedicalProfileRepository.get_json_field(profile, "allergies")

    @staticmethod
    def set_allergies(profile, allergies):
        return MedicalProfileRepository.set_json_field(profile, "allergies", allergies)

    @staticmethod
    def get_chronic_conditions(profile):
        return MedicalProfileRepository.get_json_field(profile, "chronic_conditions")

    @staticmethod
    def set_chronic_conditions(profile, chronic_conditions):
        return MedicalProfileRepository.set_json_field(
            profile,
            "chronic_conditions",
            chronic_conditions,
        )
