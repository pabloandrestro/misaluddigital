from unittest.mock import patch

from django.test import TestCase
from rest_framework import serializers

from apps.users.models import User
from apps.users.services import (
    AuthService,
    UserService,
    MedicalProfileService,
    AccountSettingsService,
    ProfileImageService,
)

# datos ficticios, ruts validos segun UserValidator.validate_rut_format
FAKE_EMAIL = "test.user@example.com"
FAKE_EMAIL_2 = "test.user2@example.com"
FAKE_RUT = "11111111-1"
FAKE_RUT_2 = "20123456-5"
FAKE_PASSWORD = "TestPass123!"
FAKE_PASSWORD_2 = "Other4567!"


def register_payload(email=FAKE_EMAIL, rut=FAKE_RUT, password=FAKE_PASSWORD, name="Test User Uno"):
    return {"email": email, "rut": rut, "password": password, "name": name}


class AuthServiceRegisterTests(TestCase):
    # 1. registro correcto
    def test_register_user_success(self):
        user = AuthService.register_user(register_payload())

        self.assertEqual(user.email, FAKE_EMAIL)
        self.assertEqual(user.rut, FAKE_RUT)
        self.assertTrue(user.check_password(FAKE_PASSWORD))

    # 2. email ya registrado
    def test_register_user_email_already_registered(self):
        AuthService.register_user(register_payload())

        with self.assertRaises(serializers.ValidationError) as ctx:
            AuthService.register_user(register_payload(rut=FAKE_RUT_2))

        self.assertIn("email", ctx.exception.detail)

    # 3. rut ya registrado
    def test_register_user_rut_already_registered(self):
        AuthService.register_user(register_payload())

        with self.assertRaises(serializers.ValidationError) as ctx:
            AuthService.register_user(register_payload(email=FAKE_EMAIL_2))

        self.assertIn("rut", ctx.exception.detail)


class AuthServiceLoginTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Test User Uno"
        )

    # 4. login correcto
    def test_login_success(self):
        user = AuthService.login(FAKE_EMAIL, FAKE_PASSWORD)

        self.assertEqual(user.id, self.user.id)

    # 5. login incorrecto (password erronea)
    def test_login_wrong_password_raises(self):
        with self.assertRaises(serializers.ValidationError) as ctx:
            AuthService.login(FAKE_EMAIL, "ContraseñaMala1!")

        self.assertIn("password", ctx.exception.detail)

    def test_login_nonexistent_user_raises(self):
        with self.assertRaises(serializers.ValidationError) as ctx:
            AuthService.login("no.existe@example.com", FAKE_PASSWORD)

        self.assertIn("email", ctx.exception.detail)

    def test_login_inactive_user_raises(self):
        self.user.is_active = False
        self.user.save()

        with self.assertRaises(serializers.ValidationError) as ctx:
            AuthService.login(FAKE_EMAIL, FAKE_PASSWORD)

        self.assertIn("user", ctx.exception.detail)


class AuthServicePasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Test User Uno"
        )

    # 6. solicitud de recuperacion para usuario existente
    def test_request_reset_existing_user(self):
        user = AuthService.request_reset(FAKE_EMAIL)

        self.assertEqual(user.id, self.user.id)

    # 7. recuperacion para usuario inexistente
    def test_request_reset_nonexistent_user_raises(self):
        with self.assertRaises(serializers.ValidationError):
            AuthService.request_reset("no.existe@example.com")

    # 8. confirmacion de recuperacion
    def test_confirm_reset_success(self):
        result = AuthService.confirm_reset(FAKE_EMAIL, FAKE_PASSWORD_2)

        self.assertTrue(result)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(FAKE_PASSWORD_2))

    # 9. contraseña nueva igual a la anterior
    def test_confirm_reset_new_password_equals_previous_raises(self):
        with self.assertRaises(serializers.ValidationError) as ctx:
            AuthService.confirm_reset(FAKE_EMAIL, FAKE_PASSWORD)

        self.assertIn("new_password", ctx.exception.detail)

    def test_confirm_reset_nonexistent_user_raises(self):
        with self.assertRaises(serializers.ValidationError):
            AuthService.confirm_reset("no.existe@example.com", FAKE_PASSWORD_2)


class UserServiceResolutionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Test User Uno"
        )

    # 10. obtener usuario por email
    def test_get_user_by_identifier_by_email(self):
        found = UserService.get_user_by_identifier(email=FAKE_EMAIL)

        self.assertEqual(found.id, self.user.id)

    # 11. obtener usuario por rut
    def test_get_user_by_identifier_by_rut(self):
        found = UserService.get_user_by_identifier(rut=FAKE_RUT)

        self.assertEqual(found.id, self.user.id)

    # 12. peticion sin email ni rut
    def test_get_user_by_identifier_without_identifier_raises(self):
        with self.assertRaises(serializers.ValidationError) as ctx:
            UserService.get_user_by_identifier()

        self.assertIn("identifier", ctx.exception.detail)

    # 13. usuario inexistente
    def test_get_user_by_identifier_nonexistent_returns_none(self):
        found = UserService.get_user_by_identifier(email="no.existe@example.com")

        self.assertIsNone(found)

    def test_validate_user_exists(self):
        self.assertTrue(UserService.validate_user_exists(self.user))
        self.assertFalse(UserService.validate_user_exists(None))


class MedicalProfileServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Test User Uno"
        )

    # 14 / 15. obtener perfil medico, se crea automaticamente si no existe
    def test_get_medical_profile_creates_if_not_exists(self):
        profile = MedicalProfileService.get_medical_profile(self.user)

        self.assertEqual(profile.user_id, self.user.id)
        self.assertEqual(profile.first_name, "")

    def test_get_medical_profile_returns_existing(self):
        first = MedicalProfileService.get_medical_profile(self.user)
        second = MedicalProfileService.get_medical_profile(self.user)

        self.assertEqual(first.pk, second.pk)

    # 16. actualizar perfil medico
    def test_update_medical_profile(self):
        profile = MedicalProfileService.update_medical_profile(
            self.user, {"first_name": "Ana", "last_name": "Soto"}
        )

        self.assertEqual(profile.first_name, "Ana")
        self.assertEqual(profile.last_name, "Soto")

    # 21. datos estructurales invalidos
    def test_update_medical_profile_invalid_data_raises(self):
        with self.assertRaises(serializers.ValidationError):
            MedicalProfileService.update_medical_profile(self.user, "no-es-un-dict")

    # 17. current_medications
    def test_set_current_medications(self):
        profile = MedicalProfileService.set_current_medications(self.user, [{"name": "Paracetamol"}])

        self.assertEqual(profile.current_medications, [{"name": "Paracetamol"}])

    # 18. recent_medical_history
    def test_set_recent_medical_history(self):
        profile = MedicalProfileService.set_recent_medical_history(self.user, [{"title": "Control"}])

        self.assertEqual(profile.recent_medical_history, [{"title": "Control"}])

    # 19. allergies
    def test_set_allergies(self):
        profile = MedicalProfileService.set_allergies(self.user, ["polen"])

        self.assertEqual(profile.allergies, ["polen"])

    # 20. chronic_conditions
    def test_set_chronic_conditions(self):
        profile = MedicalProfileService.set_chronic_conditions(self.user, ["asma"])

        self.assertEqual(profile.chronic_conditions, ["asma"])

    def test_set_current_medications_invalid_payload_raises(self):
        with self.assertRaises(serializers.ValidationError):
            MedicalProfileService.set_current_medications(self.user, "no-es-lista")


class AccountSettingsServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Nombre Original"
        )

    # 23. actualizar name
    def test_update_name(self):
        user = AccountSettingsService.update_account_settings(self.user, {"name": "Nombre Nuevo"})

        self.assertEqual(user.name, "Nombre Nuevo")

    # 24. email read-only: el service no procesa la clave "email" del payload
    def test_email_is_not_modified_by_service(self):
        original_email = self.user.email

        user = AccountSettingsService.update_account_settings(
            self.user, {"name": "Nombre Nuevo", "email": "otro@example.com"}
        )

        self.assertEqual(user.email, original_email)

    # 25. cambiar contraseña correctamente
    def test_change_password_success(self):
        user = AccountSettingsService.update_account_settings(
            self.user,
            {
                "current_password": FAKE_PASSWORD,
                "new_password": FAKE_PASSWORD_2,
                "confirm_password": FAKE_PASSWORD_2,
            },
        )

        self.assertTrue(user.check_password(FAKE_PASSWORD_2))

    # 26. contraseña actual incorrecta
    def test_change_password_wrong_current(self):
        with self.assertRaises(serializers.ValidationError) as ctx:
            AccountSettingsService.update_account_settings(
                self.user,
                {
                    "current_password": "ContraseñaMala1!",
                    "new_password": FAKE_PASSWORD_2,
                    "confirm_password": FAKE_PASSWORD_2,
                },
            )

        self.assertIn("current_password", ctx.exception.detail)

    # 27. contraseña nueva igual a la actual
    def test_change_password_new_equals_current(self):
        with self.assertRaises(serializers.ValidationError) as ctx:
            AccountSettingsService.update_account_settings(
                self.user,
                {
                    "current_password": FAKE_PASSWORD,
                    "new_password": FAKE_PASSWORD,
                    "confirm_password": FAKE_PASSWORD,
                },
            )

        self.assertIn("new_password", ctx.exception.detail)

    # nota: la comparacion new_password != confirm_password (item 28) y los
    # campos incompletos (item 29) se validan en AccountSettingsUpdateSerializer,
    # no en el service. cubiertos en tests/test_views.py contra el endpoint real.
    def test_incomplete_password_fields_are_silently_ignored_by_service(self):
        # el service solo actua si vienen los 3 campos juntos; documenta comportamiento actual
        user = AccountSettingsService.update_account_settings(
            self.user, {"current_password": FAKE_PASSWORD, "new_password": FAKE_PASSWORD_2}
        )

        self.assertTrue(user.check_password(FAKE_PASSWORD))

    def test_update_account_settings_invalid_data_raises(self):
        with self.assertRaises(serializers.ValidationError):
            AccountSettingsService.update_account_settings(self.user, "no-es-un-dict")


class ProfileImageServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Test User Uno"
        )

    # 30. obtener metadata
    def test_get_profile_image_metadata_defaults_empty(self):
        metadata = ProfileImageService.get_profile_image_metadata(self.user)

        self.assertEqual(metadata["profile_image_bucket"], "")
        self.assertEqual(metadata["profile_image_key"], "")

    # 31. subir imagen valida con storage mockeado
    @patch("apps.users.services.ProfileStorageService.upload_profile_image")
    def test_upload_user_profile_image_success(self, mock_upload):
        mock_upload.return_value = {
            "profile_image_bucket": "profile-images",
            "profile_image_key": "fake/key.jpg",
            "profile_image_url": "https://fake-storage.local/profile-images/fake/key.jpg",
        }

        profile = ProfileImageService.upload_user_profile_image(self.user, file=object())

        mock_upload.assert_called_once()
        self.assertEqual(profile.profile_image_key, "fake/key.jpg")

    # 32. reemplazar imagen existente
    @patch("apps.users.services.ProfileStorageService.delete_profile_image")
    @patch("apps.users.services.ProfileStorageService.upload_profile_image")
    def test_upload_replaces_existing_image_and_deletes_old_key(self, mock_upload, mock_delete):
        mock_upload.return_value = {
            "profile_image_bucket": "profile-images",
            "profile_image_key": "fake/first.jpg",
            "profile_image_url": "https://fake-storage.local/first.jpg",
        }
        ProfileImageService.upload_user_profile_image(self.user, file=object())

        mock_upload.return_value = {
            "profile_image_bucket": "profile-images",
            "profile_image_key": "fake/second.jpg",
            "profile_image_url": "https://fake-storage.local/second.jpg",
        }
        profile = ProfileImageService.upload_user_profile_image(self.user, file=object())

        self.assertEqual(profile.profile_image_key, "fake/second.jpg")
        mock_delete.assert_called_with("fake/first.jpg")

    # 33. eliminar imagen
    @patch("apps.users.services.ProfileStorageService.delete_profile_image")
    @patch("apps.users.services.ProfileStorageService.upload_profile_image")
    def test_delete_user_profile_image_clears_metadata(self, mock_upload, mock_delete):
        mock_upload.return_value = {
            "profile_image_bucket": "profile-images",
            "profile_image_key": "fake/key.jpg",
            "profile_image_url": "https://fake-storage.local/key.jpg",
        }
        ProfileImageService.upload_user_profile_image(self.user, file=object())

        profile = ProfileImageService.delete_user_profile_image(self.user)

        self.assertEqual(profile.profile_image_key, "")
        mock_delete.assert_called_with("fake/key.jpg")

    # 34. usuario inexistente
    def test_upload_with_none_user_raises(self):
        with self.assertRaises(serializers.ValidationError):
            ProfileImageService.upload_user_profile_image(None, file=object())

    # 35. fallo de storage sin dejar metadata inconsistente
    @patch("apps.users.services.ProfileStorageService.delete_profile_image")
    @patch("apps.users.services.ProfileStorageService.upload_profile_image")
    @patch("apps.users.services.MedicalProfileRepository.update_profile_image_metadata")
    def test_upload_db_failure_cleans_orphan_and_keeps_metadata_untouched(
        self, mock_update_metadata, mock_upload, mock_delete
    ):
        mock_upload.return_value = {
            "profile_image_bucket": "profile-images",
            "profile_image_key": "fake/new.jpg",
            "profile_image_url": "https://fake-storage.local/new.jpg",
        }
        mock_update_metadata.side_effect = Exception("fallo de base de datos")

        with self.assertRaises(Exception):
            ProfileImageService.upload_user_profile_image(self.user, file=object())

        mock_delete.assert_called_once_with("fake/new.jpg")

        metadata = ProfileImageService.get_profile_image_metadata(self.user)
        self.assertEqual(metadata["profile_image_key"], "")
