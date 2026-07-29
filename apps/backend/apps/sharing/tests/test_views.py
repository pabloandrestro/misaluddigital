import uuid
from datetime import timedelta
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.test import APITestCase


class CreateShareLinkEndpointTests(APITestCase):
    @patch("apps.sharing.views.ShareDocumentService.create_share_link")
    def test_create_share_link_success(self, mock_create):
        mock_create.return_value = {
            "token": "fake-token",
            "share_url": "http://localhost:3000/shared/fake-token",
            "expires_at": timezone.now() + timedelta(hours=24),
        }

        response = self.client.post(
            reverse("sharing-create") + "?email=share.owner@example.com",
            data={
                "professional_name": "Dr. Prueba",
                "professional_rut": "87654321-4",
                "document_ids": [str(uuid.uuid4())],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["share"]["token"], "fake-token")

    @patch("apps.sharing.views.ShareDocumentService.create_share_link")
    def test_create_share_link_validation_error(self, mock_create):
        mock_create.side_effect = ValidationError({"document_ids": ["Uno o mas documentos no existen."]})

        response = self.client.post(
            reverse("sharing-create") + "?email=share.owner@example.com",
            data={
                "professional_name": "Dr. Prueba",
                "professional_rut": "87654321-4",
                "document_ids": [str(uuid.uuid4())],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GetShareLinkEndpointTests(APITestCase):
    @patch("apps.sharing.views.ShareDocumentService.get_share_link")
    def test_get_share_link_success(self, mock_get):
        mock_get.return_value = {
            "professional_name": "Dr. Prueba",
            "professional_rut": "87654321-4",
            "expires_at": timezone.now() + timedelta(hours=1),
            "documents": [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Examen",
                    "mime_type": "application/pdf",
                    "view_url": "https://fake-storage.local/signed",
                    "expires_in": 300,
                }
            ],
        }

        response = self.client.get(reverse("sharing-get", args=["fake-token"]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["share"]["documents"]), 1)
        self.assertEqual(response.data["share"]["documents"][0]["expires_in"], 300)

    @patch("apps.sharing.views.ShareDocumentService.get_share_link")
    def test_get_share_link_not_found(self, mock_get):
        mock_get.side_effect = NotFound("Link compartido no encontrado.")

        response = self.client.get(reverse("sharing-get", args=["token-inexistente"]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("apps.sharing.views.ShareDocumentService.get_share_link")
    def test_get_share_link_expired(self, mock_get):
        mock_get.side_effect = ValidationError("El link compartido ha expirado.")

        response = self.client.get(reverse("sharing-get", args=["fake-token"]))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
