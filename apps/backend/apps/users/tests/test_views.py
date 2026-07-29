import io
import json
from unittest.mock import patch

from django.urls import reverse
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.users.models import User

FAKE_EMAIL = "test.user@example.com"
FAKE_RUT = "11111111-1"
FAKE_PASSWORD = "TestPass123!"
FAKE_PASSWORD_2 = "Other4567!"


def make_valid_image_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (400, 400), color=(120, 120, 120)).save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer.read()


class RegisterLoginEndpointTests(APITestCase):
    def test_register_success(self):
        response = self.client.post(
            reverse("register"),
            data={
                "email": FAKE_EMAIL,
                "rut": FAKE_RUT,
                "password": FAKE_PASSWORD,
                "name": "Test User Uno",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["message"], "Usuario registrado correctamente.")

    def test_register_duplicate_email(self):
        User.objects.create_user(email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Original")

        response = self.client.post(
            reverse("register"),
            data={
                "email": FAKE_EMAIL,
                "rut": "20123456-5",
                "password": FAKE_PASSWORD,
                "name": "Test User Uno",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "No se pudo crear el usuario.")

    # confirma que una excepcion interna inesperada no filtra su detalle al cliente
    @patch("apps.users.views.AuthService.register_user")
    def test_register_internal_error_does_not_leak_exception_detail(self, mock_register):
        mock_register.side_effect = Exception("internal-sensitive-test-detail")

        response = self.client.post(
            reverse("register"),
            data={
                "email": FAKE_EMAIL,
                "rut": FAKE_RUT,
                "password": FAKE_PASSWORD,
                "name": "Test User Uno",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["message"], "Ocurrio un error interno al crear el usuario.")
        self.assertNotIn("internal-sensitive-test-detail", str(response.data))
        self.assertNotIn("details", response.data)

    def test_login_success(self):
        User.objects.create_user(email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Test User Uno")

        response = self.client.post(
            reverse("login"), data={"email": FAKE_EMAIL, "password": FAKE_PASSWORD}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Inicio de sesion exitoso.")

    # bug corregido: la vista login ahora captura serializers.ValidationError
    # y responde 400 con el detalle generado por AuthService, en vez de 500.
    def test_login_wrong_password_returns_400(self):
        User.objects.create_user(email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Test User Uno")

        response = self.client.post(
            reverse("login"), data={"email": FAKE_EMAIL, "password": "ContraseñaMala1!"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "No se pudo iniciar sesion.")
        self.assertIn("password", response.data["errors"])

    def test_login_nonexistent_user_returns_400(self):
        response = self.client.post(
            reverse("login"), data={"email": "no.existe@example.com", "password": FAKE_PASSWORD}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data["errors"])

    def test_login_inactive_user_returns_400(self):
        user = User.objects.create_user(
            email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Test User Uno"
        )
        user.is_active = False
        user.save()

        response = self.client.post(
            reverse("login"), data={"email": FAKE_EMAIL, "password": FAKE_PASSWORD}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("user", response.data["errors"])

    def test_password_reset_request_existing_user(self):
        User.objects.create_user(email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Test User Uno")

        response = self.client.post(reverse("password-reset-request"), data={"email": FAKE_EMAIL})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_request_nonexistent_user(self):
        response = self.client.post(
            reverse("password-reset-request"), data={"email": "no.existe@example.com"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_success(self):
        User.objects.create_user(email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Test User Uno")

        response = self.client.post(
            reverse("password-reset-confirm"),
            data={
                "email": FAKE_EMAIL,
                "new_password": FAKE_PASSWORD_2,
                "confirm_password": FAKE_PASSWORD_2,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_confirm_new_password_equals_previous(self):
        User.objects.create_user(email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Test User Uno")

        response = self.client.post(
            reverse("password-reset-confirm"),
            data={
                "email": FAKE_EMAIL,
                "new_password": FAKE_PASSWORD,
                "confirm_password": FAKE_PASSWORD,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MeEndpointTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Test User Uno"
        )

    def test_me_by_email_query_param(self):
        response = self.client.get(reverse("me"), {"email": FAKE_EMAIL})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["email"], FAKE_EMAIL)

    def test_me_by_rut_query_param(self):
        response = self.client.get(reverse("me"), {"rut": FAKE_RUT})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_me_missing_identifier(self):
        response = self.client.get(reverse("me"))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Debe de enviar email o rut para buscar el usuario.")

    # confirma la correccion de UserResolver: me solo acepta query params
    def test_me_body_only_identifier_is_rejected(self):
        response = self.client.generic(
            "GET", reverse("me"), data=json.dumps({"email": FAKE_EMAIL}), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_me_nonexistent_user(self):
        response = self.client.get(reverse("me"), {"email": "no.existe@example.com"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["message"], "Usuario no encontrado.")


class MedicalProfileEndpointTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Test User Uno"
        )

    def test_get_medical_profile_query_param(self):
        response = self.client.get(reverse("medical-profile"), {"email": FAKE_EMAIL})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Perfil medico obtenido correctamente.")

    # medical_profile acepta identificador desde el body en PATCH
    def test_patch_medical_profile_with_identifier_in_body(self):
        response = self.client.patch(
            reverse("medical-profile"),
            data={"email": FAKE_EMAIL, "first_name": "Ana", "last_name": "Soto"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["profile"]["first_name"], "Ana")

    def test_patch_medical_profile_missing_identifier(self):
        response = self.client.patch(reverse("medical-profile"), data={"first_name": "Ana"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["message"], "Debe enviar email o rut para buscar el perfil medico."
        )

    def test_patch_medical_profile_invalid_data(self):
        response = self.client.patch(
            reverse("medical-profile"), data={"email": FAKE_EMAIL, "first_name": "123"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileImageEndpointTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Test User Uno"
        )

    def test_get_profile_image_metadata(self):
        response = self.client.get(reverse("profile-image"), {"email": FAKE_EMAIL})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch("apps.users.services.ProfileStorageService.upload_profile_image")
    def test_post_profile_image_uploads(self, mock_upload):
        mock_upload.return_value = {
            "profile_image_bucket": "profile-images",
            "profile_image_key": "fake/key.jpg",
            "profile_image_url": "https://fake-storage.local/key.jpg",
        }
        image_file = SimpleUploadedFile("foto.jpg", make_valid_image_bytes(), content_type="image/jpeg")

        response = self.client.post(
            reverse("profile-image") + f"?email={FAKE_EMAIL}",
            data={"image": image_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_upload.assert_called_once()

    @patch("apps.users.services.ProfileStorageService.delete_profile_image")
    def test_delete_profile_image(self, mock_delete):
        response = self.client.delete(reverse("profile-image"), {"email": FAKE_EMAIL})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Imagen de perfil eliminada correctamente.")

    # confirma que una excepcion interna inesperada no filtra su detalle al cliente
    @patch("apps.users.views.ProfileImageService.get_profile_image_metadata")
    def test_get_profile_image_internal_error_does_not_leak_exception_detail(self, mock_metadata):
        mock_metadata.side_effect = Exception("internal-sensitive-test-detail")

        response = self.client.get(reverse("profile-image"), {"email": FAKE_EMAIL})

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(
            response.data["message"], "Ocurrio un error interno al procesar la imagen de perfil."
        )
        self.assertNotIn("internal-sensitive-test-detail", str(response.data))
        self.assertNotIn("error", response.data)

    # confirma que las respuestas de validacion normales (400) no se vieron afectadas
    def test_post_profile_image_without_file_still_returns_real_validation_errors(self):
        response = self.client.post(
            reverse("profile-image") + f"?email={FAKE_EMAIL}",
            data={},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("image", response.data["errors"])


class AccountSettingsEndpointTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Nombre Original"
        )

    def test_get_account_settings(self):
        response = self.client.get(reverse("account-settings"), {"email": FAKE_EMAIL})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["account"]["email"], FAKE_EMAIL)

    def test_patch_name(self):
        response = self.client.patch(
            reverse("account-settings") + f"?email={FAKE_EMAIL}", data={"name": "Nombre Nuevo"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["account"]["name"], "Nombre Nuevo")

    # email read-only: el serializer de update no expone el campo email
    def test_email_is_read_only(self):
        response = self.client.patch(
            reverse("account-settings") + f"?email={FAKE_EMAIL}",
            data={"name": "Nombre Nuevo", "email": "otro@example.com"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["account"]["email"], FAKE_EMAIL)

    def test_change_password_success(self):
        response = self.client.patch(
            reverse("account-settings") + f"?email={FAKE_EMAIL}",
            data={
                "current_password": FAKE_PASSWORD,
                "new_password": FAKE_PASSWORD_2,
                "confirm_password": FAKE_PASSWORD_2,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_current_password(self):
        response = self.client.patch(
            reverse("account-settings") + f"?email={FAKE_EMAIL}",
            data={
                "current_password": "ContraseñaMala1!",
                "new_password": FAKE_PASSWORD_2,
                "confirm_password": FAKE_PASSWORD_2,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_new_password_equals_current(self):
        response = self.client.patch(
            reverse("account-settings") + f"?email={FAKE_EMAIL}",
            data={
                "current_password": FAKE_PASSWORD,
                "new_password": FAKE_PASSWORD,
                "confirm_password": FAKE_PASSWORD,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # validado por AccountSettingsUpdateSerializer, no por el service
    def test_new_passwords_do_not_match(self):
        response = self.client.patch(
            reverse("account-settings") + f"?email={FAKE_EMAIL}",
            data={
                "current_password": FAKE_PASSWORD,
                "new_password": FAKE_PASSWORD_2,
                "confirm_password": "OtraDist9!",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # validado por AccountSettingsUpdateSerializer, no por el service
    def test_incomplete_password_fields_rejected_by_serializer(self):
        response = self.client.patch(
            reverse("account-settings") + f"?email={FAKE_EMAIL}",
            data={"current_password": FAKE_PASSWORD, "new_password": FAKE_PASSWORD_2},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
