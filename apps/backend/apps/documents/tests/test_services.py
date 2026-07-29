import inspect
import re
import uuid
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.utils import timezone
from rest_framework import serializers

from apps.users.models import User
from apps.documents.models import Document, DocumentCategory
from apps.documents.services import (
    DocumentService,
    DocumentCategoryService,
    DocumentStorageService,
)

FAKE_EMAIL = "doc.owner@example.com"
FAKE_RUT = "11111111-1"
FAKE_PASSWORD = "TestPass123!"


def make_document(user, deleted_at=None, **overrides):
    # instancia en memoria, no se guarda: la tabla es managed=False y no
    # existe en la base de datos de test (ver hallazgo en informe).
    defaults = {
        "id": uuid.uuid4(),
        "user": user,
        "title": "Examen de sangre",
        "bucket_name": "documents-examenes",
        "file_key": "documents/fake/key.pdf",
        "mime_type": "application/pdf",
        "deleted_at": deleted_at,
    }
    defaults.update(overrides)
    return Document(**defaults)


def make_category(slug="examenes"):
    return DocumentCategory(id=uuid.uuid4(), name="Examenes", slug=slug)


class DocumentRepositoryCallSiteTests(TestCase):
    # cubre expresamente que DocumentService ya no llama get_by_id_and_user
    def test_get_document_by_id_and_user_uses_active_variant(self):
        source = inspect.getsource(DocumentService.get_document_by_id_and_user)

        self.assertIn("get_active_by_id_and_user", source)
        self.assertIsNone(re.search(r"get_by_id_and_user\(", source))


class DocumentServiceListTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Documento Owner"
        )

    # 1. listar documentos activos del usuario / 2. excluir eliminados
    @patch("apps.documents.services.DocumentRepository")
    def test_get_documents_by_identifier_returns_only_active(self, mock_repo):
        active_doc = make_document(self.user)
        mock_repo.get_all_by_user.return_value = [active_doc]

        documents = DocumentService.get_documents_by_identifier(email=FAKE_EMAIL)

        mock_repo.get_all_by_user.assert_called_once_with(self.user)
        self.assertEqual(list(documents), [active_doc])

    def test_get_documents_by_identifier_nonexistent_user_raises(self):
        with self.assertRaises(serializers.ValidationError):
            DocumentService.get_documents_by_identifier(email="no.existe@example.com")


class DocumentServiceCreateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Documento Owner"
        )
        self.category = make_category()

    # 3. crear documento valido con storage mockeado
    @patch("apps.documents.services.DocumentRepository")
    @patch("apps.documents.services.DocumentCategoryRepository")
    @patch("apps.documents.services.DocumentStorageService.upload_file")
    def test_create_document_success(self, mock_upload, mock_category_repo, mock_repo):
        mock_category_repo.get_by_id.return_value = self.category
        mock_upload.return_value = {
            "bucket_name": "documents-examenes",
            "file_key": "documents/fake/key.pdf",
            "file_url": None,
            "mime_type": "application/pdf",
            "file_size_bytes": 1234,
            "extracted_text": "",
        }
        created = make_document(self.user)
        mock_repo.create_document.return_value = created

        fake_file = MagicMock()
        result = DocumentService.create_document(
            self.user, {"file": fake_file, "category_id": str(self.category.id), "title": "Examen"}
        )

        self.assertEqual(result, created)
        mock_upload.assert_called_once()
        mock_repo.create_document.assert_called_once()

    def test_create_document_missing_file_raises(self):
        with self.assertRaises(serializers.ValidationError) as ctx:
            DocumentService.create_document(self.user, {"category_id": str(self.category.id)})

        self.assertIn("file", ctx.exception.detail)

    @patch("apps.documents.services.DocumentCategoryRepository")
    def test_create_document_missing_category_raises(self, mock_category_repo):
        with self.assertRaises(serializers.ValidationError) as ctx:
            DocumentService.create_document(self.user, {"file": MagicMock()})

        self.assertIn("category_id", ctx.exception.detail)

    @patch("apps.documents.services.DocumentCategoryRepository")
    def test_create_document_category_not_found_raises(self, mock_category_repo):
        mock_category_repo.get_by_id.return_value = None

        with self.assertRaises(serializers.ValidationError) as ctx:
            DocumentService.create_document(
                self.user, {"file": MagicMock(), "category_id": str(uuid.uuid4())}
            )

        self.assertIn("category_id", ctx.exception.detail)

    # 4. fallo de upload: no debe intentar insertar en bd
    @patch("apps.documents.services.DocumentRepository")
    @patch("apps.documents.services.DocumentCategoryRepository")
    @patch("apps.documents.services.DocumentStorageService.upload_file")
    def test_create_document_upload_failure_does_not_insert(self, mock_upload, mock_category_repo, mock_repo):
        mock_category_repo.get_by_id.return_value = self.category
        mock_upload.side_effect = serializers.ValidationError({"storage": "fallo de subida"})

        with self.assertRaises(serializers.ValidationError):
            DocumentService.create_document(
                self.user, {"file": MagicMock(), "category_id": str(self.category.id)}
            )

        mock_repo.create_document.assert_not_called()

    # 5. fallo de base de datos despues de upload: limpia archivo huerfano
    @patch("apps.documents.services.DocumentStorageService.delete_file")
    @patch("apps.documents.services.DocumentRepository")
    @patch("apps.documents.services.DocumentCategoryRepository")
    @patch("apps.documents.services.DocumentStorageService.upload_file")
    def test_create_document_db_failure_cleans_orphan_file(
        self, mock_upload, mock_category_repo, mock_repo, mock_delete_file
    ):
        mock_category_repo.get_by_id.return_value = self.category
        mock_upload.return_value = {
            "bucket_name": "documents-examenes",
            "file_key": "documents/fake/key.pdf",
            "file_url": None,
            "mime_type": "application/pdf",
            "file_size_bytes": 1234,
            "extracted_text": "",
        }
        mock_repo.create_document.side_effect = Exception("fallo de base de datos")

        with self.assertRaises(Exception):
            DocumentService.create_document(
                self.user, {"file": MagicMock(), "category_id": str(self.category.id)}
            )

        mock_delete_file.assert_called_once_with("documents-examenes", "documents/fake/key.pdf")


class DocumentServiceDetailTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Documento Owner"
        )

    # 6. obtener detalle de documento activo
    @patch("apps.documents.services.DocumentRepository")
    def test_get_document_by_id_and_identifier_active(self, mock_repo):
        doc = make_document(self.user)
        mock_repo.get_active_by_id_and_user.return_value = doc

        result = DocumentService.get_document_by_id_and_identifier(doc.id, email=FAKE_EMAIL)

        self.assertEqual(result, doc)
        mock_repo.get_active_by_id_and_user.assert_called_once_with(doc.id, self.user)

    # 7. documento inexistente / 8. documento de otro usuario (el repo ya filtra por owner)
    @patch("apps.documents.services.DocumentRepository")
    def test_get_document_not_found_or_not_owned_raises(self, mock_repo):
        mock_repo.get_active_by_id_and_user.return_value = None

        with self.assertRaises(serializers.ValidationError) as ctx:
            DocumentService.get_document_by_id_and_identifier(uuid.uuid4(), email=FAKE_EMAIL)

        self.assertIn("document", ctx.exception.detail)

    # 9. soft delete / 10. volver a consultar documento eliminado
    @patch("apps.documents.services.DocumentRepository")
    def test_delete_document_soft_deletes(self, mock_repo):
        doc = make_document(self.user)
        mock_repo.get_active_by_id_and_user.return_value = doc

        DocumentService.delete_document_by_id_and_identifier(doc.id, email=FAKE_EMAIL)

        mock_repo.soft_delete.assert_called_once_with(doc)

    @patch("apps.documents.services.DocumentRepository")
    def test_deleted_document_no_longer_returned_by_repo(self, mock_repo):
        # tras el soft delete, get_active_by_id_and_user (filtro deleted_at__isnull=True)
        # ya no devuelve el documento: se simula devolviendo None
        mock_repo.get_active_by_id_and_user.return_value = None

        with self.assertRaises(serializers.ValidationError):
            DocumentService.get_document_by_id_and_identifier(uuid.uuid4(), email=FAKE_EMAIL)


class DocumentServiceUrlTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=FAKE_EMAIL, password=FAKE_PASSWORD, rut=FAKE_RUT, name="Documento Owner"
        )

    # 11. generar download url
    @patch("apps.documents.services.DocumentStorageService.create_signed_url")
    @patch("apps.documents.services.DocumentRepository")
    def test_get_document_download_url(self, mock_repo, mock_signed_url):
        doc = make_document(self.user)
        mock_repo.get_active_by_id_and_user.return_value = doc
        mock_signed_url.return_value = "https://fake-storage.local/signed"

        data = DocumentService.get_document_download_url(doc.id, email=FAKE_EMAIL)

        self.assertEqual(data["download_url"], "https://fake-storage.local/signed")
        self.assertEqual(data["expires_in"], 300)

    # 12. generar view url
    @patch("apps.documents.services.DocumentStorageService.create_signed_url")
    @patch("apps.documents.services.DocumentRepository")
    def test_get_document_view_url(self, mock_repo, mock_signed_url):
        doc = make_document(self.user)
        mock_repo.get_active_by_id_and_user.return_value = doc
        mock_signed_url.return_value = "https://fake-storage.local/signed"

        data = DocumentService.get_document_view_url(doc.id, email=FAKE_EMAIL)

        self.assertEqual(data["view_url"], "https://fake-storage.local/signed")
        self.assertEqual(data["mime_type"], "application/pdf")
        self.assertEqual(data["expires_in"], 300)

    # 13. documento sin bucket o file_key
    @patch("apps.documents.services.DocumentRepository")
    def test_download_document_without_storage_metadata_raises(self, mock_repo):
        doc = make_document(self.user, bucket_name=None, file_key="")
        mock_repo.get_active_by_id_and_user.return_value = doc

        with self.assertRaises(serializers.ValidationError) as ctx:
            DocumentService.get_document_download_url(doc.id, email=FAKE_EMAIL)

        self.assertIn("document", ctx.exception.detail)

    # 14. documento eliminado no descargable
    @patch("apps.documents.services.DocumentRepository")
    def test_deleted_document_not_downloadable(self, mock_repo):
        mock_repo.get_active_by_id_and_user.return_value = None

        with self.assertRaises(serializers.ValidationError) as ctx:
            DocumentService.get_document_download_url(uuid.uuid4(), email=FAKE_EMAIL)

        self.assertIn("document", ctx.exception.detail)

    # 15. documento eliminado no visualizable
    @patch("apps.documents.services.DocumentRepository")
    def test_deleted_document_not_viewable(self, mock_repo):
        mock_repo.get_active_by_id_and_user.return_value = None

        with self.assertRaises(serializers.ValidationError) as ctx:
            DocumentService.get_document_view_url(uuid.uuid4(), email=FAKE_EMAIL)

        self.assertIn("document", ctx.exception.detail)

    def test_download_missing_identifier_raises(self):
        with self.assertRaises(serializers.ValidationError):
            DocumentService.get_document_download_url(uuid.uuid4())


class DocumentCategoryServiceTests(TestCase):
    @patch("apps.documents.services.DocumentCategoryRepository")
    def test_get_categories(self, mock_repo):
        categories = [make_category("examenes"), make_category("recetas-medicas")]
        mock_repo.get_all.return_value = categories

        result = DocumentCategoryService.get_categories()

        self.assertEqual(result, categories)

    @patch("apps.documents.services.DocumentCategoryRepository")
    def test_get_category_by_id_not_found_raises(self, mock_repo):
        mock_repo.get_by_id.return_value = None

        with self.assertRaises(serializers.ValidationError):
            DocumentCategoryService.get_category_by_id(uuid.uuid4())


class DocumentStorageServiceTests(TestCase):
    def test_get_bucket_by_category_known_slug(self):
        category = make_category("examenes")

        bucket = DocumentStorageService.get_bucket_by_category(category)

        self.assertEqual(bucket, "documents-examenes")

    def test_get_bucket_by_category_unknown_slug_raises(self):
        category = make_category("slug-inexistente")

        with self.assertRaises(serializers.ValidationError):
            DocumentStorageService.get_bucket_by_category(category)

    @patch("apps.documents.services.DocumentStorageService.get_supabase_client")
    def test_delete_file_swallows_storage_errors(self, mock_get_client):
        mock_client = MagicMock()
        mock_client.storage.from_.return_value.remove.side_effect = Exception("network error")
        mock_get_client.return_value = mock_client

        # no debe lanzar excepcion aunque supabase falle
        DocumentStorageService.delete_file("bucket", "key")

    def test_delete_file_noop_without_bucket_or_key(self):
        # no debe intentar crear cliente si falta bucket o key
        DocumentStorageService.delete_file(None, None)
        DocumentStorageService.delete_file("bucket", None)
