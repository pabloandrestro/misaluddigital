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