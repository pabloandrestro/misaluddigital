import uuid
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError

from apps.users.services import UserService
from apps.documents.models import Document
from apps.documents.services import DocumentStorageService
from .serializers import ShareDocumentSerializer
from .repositories import TemporaryAccessLinkRepository


class ShareDocumentService:

    # crea un enlace de acceso temporal para compartir documentos
    @staticmethod
    def create_share_link(email=None, rut=None, data=None):
        if not email and not rut:
            raise ValidationError({
                "user": ["email o rut obligatorio para identificar al usuario."]
            })

        # buscar y validar usuario
        try:
            user = UserService.get_user_by_identifier(email=email, rut=rut)
            if not user:
                raise ValidationError({
                    "user": ["El usuario no existe."]
                })
        except Exception:
            raise ValidationError({
                "user": ["El usuario no existe."]
            })

        # validar datos del profesional y expiracion
        serializer = ShareDocumentSerializer(data=data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        document_ids = serializer.validated_data["document_ids"]

        # validar pertenencia, existencia y estado de los documentos
        for doc_id in document_ids:
            doc = Document.objects.filter(id=doc_id).first()
            if not doc:
                raise ValidationError({
                    "document_ids": ["Uno o mas documentos no existen."]
                })

            if doc.deleted_at is not None:
                raise ValidationError({
                    "document_ids": ["No se pueden compartir documentos eliminados."]
                })

            if doc.user_id != user.id:
                raise ValidationError({
                    "document_ids": ["No se pueden compartir documentos de otro usuario."]
                })

        # generar token unico
        token = uuid.uuid4().hex
        while TemporaryAccessLinkRepository.get_by_token(token) is not None:
            token = uuid.uuid4().hex

        # calcular fecha de expiracion
        expires_in_hours = serializer.validated_data["expires_in_hours"]
        expires_at = timezone.now() + timedelta(hours=expires_in_hours)

        # persistir en base de datos
        link_data = {
            "user": user,
            "token": token,
            "professional_name": serializer.validated_data["professional_name"],
            "professional_rut": serializer.validated_data["professional_rut"],
            "document_ids": document_ids,
            "expires_at": expires_at
        }
        link = TemporaryAccessLinkRepository.create(link_data)

        # construir la url de compartir usando el frontend url
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
        share_url = f"{frontend_url.rstrip('/')}/shared/{token}"

        return {
            "token": token,
            "share_url": share_url,
            "expires_at": expires_at
        }

    # obtiene y valida un enlace temporal por token para visualizar documentos
    @staticmethod
    def get_share_link(token):
        link = TemporaryAccessLinkRepository.get_by_token(token)
        if not link:
            raise NotFound("Link compartido no encontrado.")

        # validar si el enlace expiro
        if link.expires_at < timezone.now():
            raise ValidationError("El link compartido ha expirado.")

        # registrar la primera fecha de acceso si no existe
        if link.accessed_at is None:
            link.accessed_at = timezone.now()
            TemporaryAccessLinkRepository.save(link)

        # buscar y generar signed urls para documentos asociados
        documents_list = []
        for doc_id in link.document_ids:
            doc = Document.objects.filter(
                id=doc_id,
                user=link.user,
                deleted_at__isnull=True
            ).first()
            if doc:
                signed_url = DocumentStorageService.create_signed_url(
                    doc.bucket_name,
                    doc.file_key,
                    expires_in=300
                )
                documents_list.append({
                    "id": str(doc.id),
                    "title": doc.title,
                    "mime_type": doc.mime_type,
                    "view_url": signed_url,
                    "expires_in": 300
                })

        return {
            "professional_name": link.professional_name,
            "professional_rut": link.professional_rut,
            "expires_at": link.expires_at,
            "documents": documents_list
        }
