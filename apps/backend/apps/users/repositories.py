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

    # todo: implementar cuando profile_image_bucket, profile_image_key y profile_image_url existan en el modelo
    @staticmethod
    def update_profile_image_metadata(profile, profile_image_bucket, profile_image_key, profile_image_url=""):
        pass

    # todo: implementar limpieza de metadata de foto de perfil
    @staticmethod
    def clear_profile_image_metadata(profile):
        pass

    # todo: implementar lectura de metadata de foto de perfil
    @staticmethod
    def get_profile_image_metadata(profile):
        pass

    # todo: implementar lectura generica de jsonfield por nombre de campo
    @staticmethod
    def get_json_field(profile, field_name):
        pass

    # todo: implementar escritura generica de jsonfield por nombre de campo
    @staticmethod
    def set_json_field(profile, field_name, value):
        pass

    # todo: implementar cuando current_medications exista en el modelo
    @staticmethod
    def get_current_medications(profile):
        pass

    # todo: implementar cuando current_medications exista en el modelo
    @staticmethod
    def set_current_medications(profile, medications):
        pass

    # todo: implementar cuando recent_medical_history exista en el modelo
    @staticmethod
    def get_recent_medical_history(profile):
        pass

    # todo: implementar cuando recent_medical_history exista en el modelo
    @staticmethod
    def set_recent_medical_history(profile, history):
        pass

    # todo: implementar cuando allergies exista en el modelo
    @staticmethod
    def get_allergies(profile):
        pass

    # todo: implementar cuando allergies exista en el modelo
    @staticmethod
    def set_allergies(profile, allergies):
        pass

    # todo: implementar cuando chronic_conditions exista en el modelo
    @staticmethod
    def get_chronic_conditions(profile):
        pass

    # todo: implementar cuando chronic_conditions exista en el modelo
    @staticmethod
    def set_chronic_conditions(profile, chronic_conditions):
        pass
