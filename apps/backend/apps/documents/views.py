from rest_framework import status, serializers
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import (
    DocumentSerializer,
    CreateDocumentSerializer,
    DocumentCategorySerializer,
)

from .services import (
    DocumentService,
    DocumentCategoryService,
)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def documents_view(request):
    try:
        email = request.query_params.get("email")
        rut = request.query_params.get("rut")

        if request.method == "GET":
            # listar documentos del usuario
            documents = DocumentService.get_documents_by_identifier(
                email=email,
                rut=rut
            )

            response_serializer = DocumentSerializer(documents, many=True)

            return Response({
                "status": "success",
                "message": "Documentos obtenidos correctamente.",
                "documents": response_serializer.data
            }, status=status.HTTP_200_OK)

        if request.method == "POST":
            # crear o subir documento
            serializer = CreateDocumentSerializer(data=request.data)

            if not serializer.is_valid():
                return Response({
                    "status": "error",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            data = serializer.validated_data.copy()
            # aplanar listas de un solo elemento de multipart
            for key in data:
                if isinstance(data[key], list) and len(data[key]) == 1:
                    data[key] = data[key][0]

            document = DocumentService.create_document_by_identifier(
                email=email,
                rut=rut,
                data=data
            )

            return Response({
                "status": "success",
                "message": "Documento creado correctamente.",
                "document_id": str(document.id)
            }, status=status.HTTP_201_CREATED)

    except serializers.ValidationError as error:
        return Response({
            "status": "error",
            "errors": error.detail
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception:
        return Response({
            "status": "error",
            "message": "Error interno del servidor."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([AllowAny])
def document_detail_view(request, document_id):
    try:
        email = request.query_params.get("email")
        rut = request.query_params.get("rut")

        if request.method == "GET":
            # obtener detalle del documento
            document = DocumentService.get_document_by_id_and_identifier(
                document_id=document_id,
                email=email,
                rut=rut
            )

            response_serializer = DocumentSerializer(document)

            return Response({
                "status": "success",
                "message": "Documento obtenido correctamente.",
                "document": response_serializer.data
            }, status=status.HTTP_200_OK)

        if request.method == "PUT":
            # actualizacion no implementada aun
            return Response({
                "status": "error",
                "message": "Actualizacion de documento no implementada aun."
            }, status=status.HTTP_501_NOT_IMPLEMENTED)

        if request.method == "DELETE":
            # eliminar documento con soft delete
            DocumentService.delete_document_by_id_and_identifier(
                document_id=document_id,
                email=email,
                rut=rut
            )

            return Response({
                "status": "success",
                "message": "Documento eliminado correctamente."
            }, status=status.HTTP_200_OK)

    except serializers.ValidationError as error:
        return Response({
            "status": "error",
            "errors": error.detail
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception:
        return Response({
            "status": "error",
            "message": "Error interno del servidor."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
@permission_classes([AllowAny])
def document_categories_view(request):
    try:
        # listar categorias de documentos
        categories = DocumentCategoryService.get_categories()

        response_serializer = DocumentCategorySerializer(
            categories, many=True
        )

        return Response({
            "status": "success",
            "message": "Categorias obtenidas correctamente.",
            "categories": response_serializer.data
        }, status=status.HTTP_200_OK)

    except Exception:
        return Response({
            "status": "error",
            "message": "Error interno del servidor."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
