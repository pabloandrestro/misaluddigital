import uuid
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import serializers, status
from rest_framework.test import APITestCase

from apps.documents.models import Document, DocumentCategory


def make_document(**overrides):
    defaults = {
        "id": uuid.uuid4(),
        "title": "Examen de sangre",
        "bucket_name": "documents-examenes",
        "file_key": "documents/fake/key.pdf",
        "file_url": None,
        "mime_type": "application/pdf",
        "file_size_bytes": 1024,
        "deleted_at": None,
    }
    defaults.update(overrides)
    doc = Document(**defaults)
    doc.category = None
    return doc


def make_category():
    return DocumentCategory(id=uuid.uuid4(), name="Examenes", slug="examenes", icon="flask")


class DocumentsListCreateEndpointTests(APITestCase):
    @patch("apps.documents.views.DocumentService.get_documents_by_identifier")
    def test_list_documents_success(self, mock_list):
        mock_list.return_value = [make_document()]

        response = self.client.get(reverse("documents"), {"email": "doc.owner@example.com"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Documentos obtenidos correctamente.")
        self.assertEqual(len(response.data["documents"]), 1)

    @patch("apps.documents.views.DocumentService.get_documents_by_identifier")
    def test_list_documents_nonexistent_user(self, mock_list):
        mock_list.side_effect = serializers.ValidationError({"user": "El usuario no existe."})

        response = self.client.get(reverse("documents"), {"email": "no.existe@example.com"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.documents.views.DocumentService.create_document_by_identifier")
    def test_create_document_success(self, mock_create):
        mock_create.return_value = make_document()
        pdf_file = SimpleUploadedFile("receta.pdf", b"%PDF-1.4 fake content", content_type="application/pdf")

        response = self.client.post(
            reverse("documents") + "?email=doc.owner@example.com",
            data={"title": "Receta", "document_type": "prescription", "file": pdf_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("document_id", response.data)

    def test_create_document_missing_file_returns_400(self):
        response = self.client.post(
            reverse("documents") + "?email=doc.owner@example.com",
            data={"title": "Receta", "document_type": "prescription"},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DocumentDetailEndpointTests(APITestCase):
    @patch("apps.documents.views.DocumentService.get_document_by_id_and_identifier")
    def test_get_document_detail_success(self, mock_get):
        doc = make_document()
        mock_get.return_value = doc

        response = self.client.get(
            reverse("document_detail", args=[doc.id]), {"email": "doc.owner@example.com"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["document"]["id"], str(doc.id))

    @patch("apps.documents.views.DocumentService.get_document_by_id_and_identifier")
    def test_get_document_detail_not_found(self, mock_get):
        mock_get.side_effect = serializers.ValidationError(
            {"document": "El documento no existe o no pertenece al usuario."}
        )

        response = self.client.get(
            reverse("document_detail", args=[uuid.uuid4()]), {"email": "doc.owner@example.com"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # documento de otro usuario: mismo contrato que documento inexistente
    @patch("apps.documents.views.DocumentService.get_document_by_id_and_identifier")
    def test_get_document_of_another_user_rejected(self, mock_get):
        mock_get.side_effect = serializers.ValidationError(
            {"document": "El documento no existe o no pertenece al usuario."}
        )

        response = self.client.get(
            reverse("document_detail", args=[uuid.uuid4()]), {"email": "otro.usuario@example.com"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.documents.views.DocumentService.delete_document_by_id_and_identifier")
    def test_delete_document_success(self, mock_delete):
        response = self.client.delete(
            reverse("document_detail", args=[uuid.uuid4()]), {"email": "doc.owner@example.com"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Documento eliminado correctamente.")

    def test_put_document_not_implemented(self):
        response = self.client.put(
            reverse("document_detail", args=[uuid.uuid4()]), {"email": "doc.owner@example.com"}
        )

        self.assertEqual(response.status_code, status.HTTP_501_NOT_IMPLEMENTED)


class DocumentCategoriesEndpointTests(APITestCase):
    @patch("apps.documents.views.DocumentCategoryService.get_categories")
    def test_list_categories(self, mock_get):
        mock_get.return_value = [make_category()]

        response = self.client.get(reverse("document_categories"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["categories"]), 1)


class DocumentUrlEndpointTests(APITestCase):
    # contrato: signed urls usan expiracion actual de 300 segundos
    @patch("apps.documents.views.DocumentService.get_document_download_url")
    def test_download_url_uses_300_seconds_expiration(self, mock_download):
        mock_download.return_value = {
            "download_url": "https://fake-storage.local/signed",
            "expires_in": 300,
        }

        response = self.client.get(
            reverse("document-download", args=[uuid.uuid4()]), {"email": "doc.owner@example.com"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["expires_in"], 300)

    @patch("apps.documents.views.DocumentService.get_document_view_url")
    def test_view_url_uses_300_seconds_expiration(self, mock_view):
        mock_view.return_value = {
            "view_url": "https://fake-storage.local/signed",
            "mime_type": "application/pdf",
            "expires_in": 300,
        }

        response = self.client.get(
            reverse("document_view_view", args=[uuid.uuid4()]), {"email": "doc.owner@example.com"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["expires_in"], 300)

    # documento eliminado no descargable ni visualizable a nivel endpoint
    @patch("apps.documents.views.DocumentService.get_document_download_url")
    def test_download_deleted_document_blocked(self, mock_download):
        mock_download.side_effect = serializers.ValidationError({"document": "Documento no encontrado."})

        response = self.client.get(
            reverse("document-download", args=[uuid.uuid4()]), {"email": "doc.owner@example.com"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("apps.documents.views.DocumentService.get_document_view_url")
    def test_view_deleted_document_blocked(self, mock_view):
        mock_view.side_effect = serializers.ValidationError({"document": "Documento no encontrado."})

        response = self.client.get(
            reverse("document_view_view", args=[uuid.uuid4()]), {"email": "doc.owner@example.com"}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
