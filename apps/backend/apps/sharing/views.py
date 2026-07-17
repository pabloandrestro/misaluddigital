import uuid
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.users.services import UserService
from apps.documents.models import Document
from apps.documents.services import DocumentStorageService
from .serializers import ShareDocumentSerializer
from .repositories import TemporaryAccessLinkRepository


@api_view(["POST"])
@permission_classes([AllowAny])
def create_share_link(request):
    # buscar usuario por email o rut en query params
    email = request.query_params.get("email")
    rut = request.query_params.get("rut")

    if not email and not rut:
        return Response({
            "status": "error",
            "message": "Datos invalidos.",
            "errors": {
                "user": ["email o rut obligatorio para identificar al usuario."]
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = UserService.get_user_by_identifier(email=email, rut=rut)
        if not user:
            return Response({
                "status": "error",
                "message": "Datos invalidos.",
                "errors": {
                    "user": ["El usuario no existe."]
                }
            }, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({
            "status": "error",
            "message": "Datos invalidos.",
            "errors": {
                "user": ["El usuario no existe."]
            }
        }, status=status.HTTP_400_BAD_REQUEST)

    # validar los datos del profesional y de expiracion
    serializer = ShareDocumentSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": "Datos invalidos.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    document_ids = serializer.validated_data["document_ids"]

    # validar pertenencia, existencia y estado de documentos
    for doc_id in document_ids:
        doc = Document.objects.filter(id=doc_id).first()
        if not doc:
            return Response({
                "status": "error",
                "message": "Datos invalidos.",
                "errors": {
                    "document_ids": ["Uno o mas documentos no existen."]
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        if doc.deleted_at is not None:
            return Response({
                "status": "error",
                "message": "Datos invalidos.",
                "errors": {
                    "document_ids": ["No se pueden compartir documentos eliminados."]
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        if doc.user_id != user.id:
            return Response({
                "status": "error",
                "message": "Datos invalidos.",
                "errors": {
                    "document_ids": ["No se pueden compartir documentos de otro usuario."]
                }
            }, status=status.HTTP_400_BAD_REQUEST)

    # generar token unico
    token = uuid.uuid4().hex
    while TemporaryAccessLinkRepository.get_by_token(token) is not None:
        token = uuid.uuid4().hex

    # calcular fecha de expiracion
    expires_in_hours = serializer.validated_data["expires_in_hours"]
    expires_at = timezone.now() + timedelta(hours=expires_in_hours)

    # crear el enlace temporal en base de datos
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

    return Response({
        "status": "success",
        "message": "Link compartido creado correctamente.",
        "share": {
            "token": token,
            "share_url": share_url,
            "expires_at": expires_at.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_share_link(request, token):
    # buscar el enlace temporal por token
    link = TemporaryAccessLinkRepository.get_by_token(token)
    if not link:
        return Response({
            "status": "error",
            "message": "Link compartido no encontrado."
        }, status=status.HTTP_404_NOT_FOUND)

    # validar si el enlace expiro
    if link.expires_at < timezone.now():
        return Response({
            "status": "error",
            "message": "El link compartido ha expirado."
        }, status=status.HTTP_400_BAD_REQUEST)

    # registrar la primera fecha de acceso si no existe
    if link.accessed_at is None:
        link.accessed_at = timezone.now()
        TemporaryAccessLinkRepository.save(link)

    # buscar y generar signed urls para documentos asociados
    documents_list = []
    for doc_id in link.document_ids:
        doc = Document.objects.filter(id=doc_id, deleted_at__isnull=True).first()
        if doc:
            # firmar url temporal del storage de supabase por 5 minutos
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

    return Response({
        "status": "success",
        "share": {
            "professional_name": link.professional_name,
            "professional_rut": link.professional_rut,
            "expires_at": link.expires_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "documents": documents_list
        }
    }, status=status.HTTP_200_OK)
