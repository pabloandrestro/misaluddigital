import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from apps.users.models import User
from apps.sharing.services import ShareDocumentService
from apps.sharing.serializers import ShareDocumentSerializer

FAKE_EMAIL = "share.owner@example.com"
FAKE_RUT = "11111111-1"
FAKE_PASSWORD = "TestPass123!"
FAKE_PROFESSIONAL_RUT = "87654321-4"


def make_fake_document(doc_id, user_id, deleted_at=None):
    doc = MagicMock()
    doc.id = doc_id
    doc.user_id = user_id
    doc.deleted_at = deleted_at
    doc.title = "Examen de sangre"
    doc.mime_type = "application/pdf"
    doc.bucket_name = "documents-examenes"
    doc.file_key = "documents/fake/key.pdf"
    return doc


def documents_lookup_mock(docs_by_id):
    def filter_side_effect(**kwargs):
        result = MagicMock()
        doc_id = kwargs.get("id")
        user = kwargs.get("user")
        doc = docs_by_id.get(doc_id)
        if user is not None and doc is not None and doc.user_id != user.id:
            doc = None
        if "deleted_at__isnull" in kwargs and doc is not None and doc.deleted_at is not None:
            doc = None
        result.first.return_value = doc
        return result

    mock_objects = MagicMock()
    mock_objects.filter.side_effect = filter_side_effect
    return mock_objects


class ShareDocumentServiceCreateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Share Owner"
        )
        self.doc_id = uuid.uuid4()

    def payload(self, **overrides):
        data = {
            "professional_name": "Dr. Prueba",
            "professional_rut": FAKE_PROFESSIONAL_RUT,
            "document_ids": [str(self.doc_id)],
        }
        data.update(overrides)
        return data

    # 1. crear link con un documento propio
    @patch("apps.sharing.services.TemporaryAccessLinkRepository")
    @patch("apps.sharing.services.Document")
    def test_create_share_link_single_document(self, mock_document_cls, mock_repo):
        doc = make_fake_document(self.doc_id, self.user.id)
        mock_document_cls.objects = documents_lookup_mock({self.doc_id: doc})
        mock_repo.get_by_token.return_value = None
        mock_repo.create.return_value = MagicMock()

        result = ShareDocumentService.create_share_link(email=FAKE_EMAIL, data=self.payload())

        self.assertIn("token", result)
        self.assertIn("share_url", result)
        mock_repo.create.assert_called_once()

    # 2. crear link con varios documentos propios
    @patch("apps.sharing.services.TemporaryAccessLinkRepository")
    @patch("apps.sharing.services.Document")
    def test_create_share_link_multiple_documents(self, mock_document_cls, mock_repo):
        doc_id_2 = uuid.uuid4()
        doc1 = make_fake_document(self.doc_id, self.user.id)
        doc2 = make_fake_document(doc_id_2, self.user.id)
        mock_document_cls.objects = documents_lookup_mock({self.doc_id: doc1, doc_id_2: doc2})
        mock_repo.get_by_token.return_value = None
        mock_repo.create.return_value = MagicMock()

        result = ShareDocumentService.create_share_link(
            email=FAKE_EMAIL, data=self.payload(document_ids=[str(self.doc_id), str(doc_id_2)])
        )

        self.assertIn("token", result)

    # 3. expiracion por defecto de 24 horas
    @patch("apps.sharing.services.TemporaryAccessLinkRepository")
    @patch("apps.sharing.services.Document")
    def test_create_share_link_default_expiration_24_hours(self, mock_document_cls, mock_repo):
        doc = make_fake_document(self.doc_id, self.user.id)
        mock_document_cls.objects = documents_lookup_mock({self.doc_id: doc})
        mock_repo.get_by_token.return_value = None
        mock_repo.create.return_value = MagicMock()

        before = timezone.now()
        result = ShareDocumentService.create_share_link(email=FAKE_EMAIL, data=self.payload())
        after = timezone.now()

        expected_min = before + timedelta(hours=24)
        expected_max = after + timedelta(hours=24)
        self.assertTrue(expected_min <= result["expires_at"] <= expected_max)

    # 4. rechazar document_ids vacio
    def test_create_share_link_empty_document_ids_rejected(self):
        with self.assertRaises(ValidationError):
            ShareDocumentService.create_share_link(email=FAKE_EMAIL, data=self.payload(document_ids=[]))

    # 5. rechazar documento inexistente
    @patch("apps.sharing.services.Document")
    def test_create_share_link_document_not_found(self, mock_document_cls):
        mock_document_cls.objects = documents_lookup_mock({})

        with self.assertRaises(ValidationError) as ctx:
            ShareDocumentService.create_share_link(email=FAKE_EMAIL, data=self.payload())

        self.assertIn("document_ids", ctx.exception.detail)

    # 6. rechazar documento eliminado
    @patch("apps.sharing.services.Document")
    def test_create_share_link_deleted_document_rejected(self, mock_document_cls):
        doc = make_fake_document(self.doc_id, self.user.id, deleted_at=timezone.now())
        mock_objects = MagicMock()
        mock_objects.filter.return_value.first.return_value = doc
        mock_document_cls.objects = mock_objects

        with self.assertRaises(ValidationError) as ctx:
            ShareDocumentService.create_share_link(email=FAKE_EMAIL, data=self.payload())

        self.assertIn("document_ids", ctx.exception.detail)

    # 7. rechazar documento de otro usuario
    @patch("apps.sharing.services.Document")
    def test_create_share_link_other_user_document_rejected(self, mock_document_cls):
        other_user_id = uuid.uuid4()
        doc = make_fake_document(self.doc_id, other_user_id)
        mock_objects = MagicMock()
        mock_objects.filter.return_value.first.return_value = doc
        mock_document_cls.objects = mock_objects

        with self.assertRaises(ValidationError) as ctx:
            ShareDocumentService.create_share_link(email=FAKE_EMAIL, data=self.payload())

        self.assertIn("document_ids", ctx.exception.detail)

    def test_create_share_link_missing_identifier_raises(self):
        with self.assertRaises(ValidationError):
            ShareDocumentService.create_share_link(data=self.payload())

    def test_create_share_link_nonexistent_user_raises(self):
        with self.assertRaises(ValidationError):
            ShareDocumentService.create_share_link(email="no.existe@example.com", data=self.payload())


class ShareDocumentServiceGetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Share Owner"
        )
        self.doc_id = uuid.uuid4()
        self.token = "fake-token-1234"

    def make_link(self, expires_at=None, accessed_at=None, document_ids=None):
        link = MagicMock()
        link.token = self.token
        link.user = self.user
        link.expires_at = expires_at or (timezone.now() + timedelta(hours=1))
        link.accessed_at = accessed_at
        link.document_ids = document_ids if document_ids is not None else [self.doc_id]
        link.professional_name = "Dr. Prueba"
        link.professional_rut = FAKE_PROFESSIONAL_RUT
        return link

    # 8. obtener link valido
    @patch("apps.sharing.services.DocumentStorageService.create_signed_url")
    @patch("apps.sharing.services.Document")
    @patch("apps.sharing.services.TemporaryAccessLinkRepository")
    def test_get_share_link_valid(self, mock_repo, mock_document_cls, mock_signed_url):
        link = self.make_link()
        mock_repo.get_by_token.return_value = link
        doc = make_fake_document(self.doc_id, self.user.id)
        mock_objects = MagicMock()
        mock_objects.filter.return_value.first.return_value = doc
        mock_document_cls.objects = mock_objects
        mock_signed_url.return_value = "https://fake-storage.local/signed"

        result = ShareDocumentService.get_share_link(self.token)

        self.assertEqual(len(result["documents"]), 1)
        self.assertEqual(result["documents"][0]["expires_in"], 300)
        mock_repo.save.assert_called_once()

    # 9. token inexistente
    @patch("apps.sharing.services.TemporaryAccessLinkRepository")
    def test_get_share_link_token_not_found(self, mock_repo):
        mock_repo.get_by_token.return_value = None

        with self.assertRaises(NotFound):
            ShareDocumentService.get_share_link("token-inexistente")

    # 10. token expirado
    @patch("apps.sharing.services.TemporaryAccessLinkRepository")
    def test_get_share_link_expired(self, mock_repo):
        expired_link = self.make_link(expires_at=timezone.now() - timedelta(hours=1))
        mock_repo.get_by_token.return_value = expired_link

        with self.assertRaises(ValidationError):
            ShareDocumentService.get_share_link(self.token)

    # 11. generar view_url con storage mockeado
    @patch("apps.sharing.services.DocumentStorageService.create_signed_url")
    @patch("apps.sharing.services.Document")
    @patch("apps.sharing.services.TemporaryAccessLinkRepository")
    def test_get_share_link_generates_signed_url(self, mock_repo, mock_document_cls, mock_signed_url):
        link = self.make_link()
        mock_repo.get_by_token.return_value = link
        doc = make_fake_document(self.doc_id, self.user.id)
        mock_objects = MagicMock()
        mock_objects.filter.return_value.first.return_value = doc
        mock_document_cls.objects = mock_objects
        mock_signed_url.return_value = "https://fake-storage.local/signed"

        result = ShareDocumentService.get_share_link(self.token)

        mock_signed_url.assert_called_once_with(doc.bucket_name, doc.file_key, expires_in=300)
        self.assertEqual(result["documents"][0]["view_url"], "https://fake-storage.local/signed")

    # 12. devolver solamente documentos autorizados
    @patch("apps.sharing.services.DocumentStorageService.create_signed_url")
    @patch("apps.sharing.services.Document")
    @patch("apps.sharing.services.TemporaryAccessLinkRepository")
    def test_get_share_link_excludes_unauthorized_documents(
        self, mock_repo, mock_document_cls, mock_signed_url
    ):
        other_doc_id = uuid.uuid4()
        link = self.make_link(document_ids=[self.doc_id, other_doc_id])
        mock_repo.get_by_token.return_value = link
        doc = make_fake_document(self.doc_id, self.user.id)
        # la query real filtra por user=link.user y deleted_at__isnull=True;
        # el segundo id no pertenece al usuario del link y no aparece
        mock_objects = MagicMock()
        mock_objects.filter.return_value.first.side_effect = [doc, None]
        mock_document_cls.objects = mock_objects
        mock_signed_url.return_value = "https://fake-storage.local/signed"

        result = ShareDocumentService.get_share_link(self.token)

        self.assertEqual(len(result["documents"]), 1)
        self.assertEqual(result["documents"][0]["id"], str(self.doc_id))


class ProfessionalNameLengthTests(TestCase):
    # confirma el limite real de la columna (schema.sql: varchar(150))
    def setUp(self):
        self.user = User.objects.create_user(
            email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Share Owner"
        )
        self.doc_id = uuid.uuid4()

    def payload(self, **overrides):
        data = {
            "professional_name": "Dr. Prueba",
            "professional_rut": FAKE_PROFESSIONAL_RUT,
            "document_ids": [str(self.doc_id)],
        }
        data.update(overrides)
        return data

    # 1. professional_name de 150 caracteres es aceptado por el serializer
    def test_professional_name_150_characters_is_valid(self):
        serializer = ShareDocumentSerializer(data=self.payload(professional_name="A" * 150))

        self.assertTrue(serializer.is_valid())
        self.assertNotIn("professional_name", serializer.errors)

    # 2. professional_name de 151 caracteres es rechazado, con el mensaje real de DRF
    def test_professional_name_151_characters_is_invalid(self):
        serializer = ShareDocumentSerializer(data=self.payload(professional_name="A" * 151))

        self.assertFalse(serializer.is_valid())
        self.assertIn("professional_name", serializer.errors)
        self.assertIn(
            "150",
            str(serializer.errors["professional_name"][0]),
        )

    # 3. el service no llega a tocar Document ni el repository cuando el nombre es invalido
    @patch("apps.sharing.services.TemporaryAccessLinkRepository")
    @patch("apps.sharing.services.Document")
    def test_create_share_link_does_not_touch_repository_when_name_too_long(
        self, mock_document_cls, mock_repo
    ):
        with self.assertRaises(ValidationError) as ctx:
            ShareDocumentService.create_share_link(
                email=FAKE_EMAIL, data=self.payload(professional_name="A" * 151)
            )

        self.assertIn("professional_name", ctx.exception.detail)
        mock_document_cls.objects.filter.assert_not_called()
        mock_repo.create.assert_not_called()

    # 4. via API real: 400 con el mismo mensaje del serializer
    def test_create_share_link_api_returns_400_for_151_characters(self):
        from django.urls import reverse
        from rest_framework.test import APIClient

        client = APIClient()
        response = client.post(
            reverse("sharing-create") + f"?email={FAKE_EMAIL}",
            data=self.payload(professional_name="A" * 151),
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "150",
            str(response.data["errors"]["professional_name"][0]),
        )
