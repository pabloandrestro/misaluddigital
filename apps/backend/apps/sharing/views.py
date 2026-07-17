from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError

from .services import ShareDocumentService


@api_view(["POST"])
@permission_classes([AllowAny])
def create_share_link(request):
    # buscar usuario por email o rut en query params
    email = request.query_params.get("email")
    rut = request.query_params.get("rut")

    try:
        share_data = ShareDocumentService.create_share_link(
            email=email,
            rut=rut,
            data=request.data
        )
        return Response({
            "status": "success",
            "message": "Link compartido creado correctamente.",
            "share": {
                "token": share_data["token"],
                "share_url": share_data["share_url"],
                "expires_at": share_data["expires_at"].strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        }, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response({
            "status": "error",
            "message": "Datos invalidos.",
            "errors": e.detail
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_share_link(request, token):
    try:
        share_data = ShareDocumentService.get_share_link(token)
        return Response({
            "status": "success",
            "share": {
                "professional_name": share_data["professional_name"],
                "professional_rut": share_data["professional_rut"],
                "expires_at": share_data["expires_at"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "documents": share_data["documents"]
            }
        }, status=status.HTTP_200_OK)
    except NotFound as e:
        # e.detail puede ser una lista o string, obtenemos el valor legible
        msg = e.detail[0] if isinstance(e.detail, list) else str(e.detail)
        return Response({
            "status": "error",
            "message": msg
        }, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
        # e.detail puede ser una lista, un dict o un string
        if isinstance(e.detail, dict) and "message" in e.detail:
            msg = e.detail["message"]
            msg_str = msg[0] if isinstance(msg, list) else str(msg)
        elif isinstance(e.detail, list):
            msg_str = e.detail[0]
        else:
            msg_str = str(e.detail)
            
        return Response({
            "status": "error",
            "message": msg_str
        }, status=status.HTTP_400_BAD_REQUEST)
