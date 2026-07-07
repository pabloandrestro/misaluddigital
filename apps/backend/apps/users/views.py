from rest_framework import status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .services import UserService
from apps.users.services import AuthService
from apps.users.serializers import (
    UserSerializer,
    LoginSerializer,
    RegisterSerializer,
    MedicalProfileSerializer,
    ProfileImageUploadSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
)


# --------------------------
# parte del Auth
# --------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": "Datos invalidos.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = UserService.register_user(serializer.validated_data)

        if user is None:
            return Response({
                "status": "error",
                "message": "No se pudo crear el usuario."
            }, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = UserSerializer(user)

        return Response({
            "status": "success",
            "message": "Usuario registrado correctamente.",
            "user": response_serializer.data
        }, status=status.HTTP_201_CREATED)

    except serializers.ValidationError as error:
        return Response({
            "status": "error",
            "message": "No se pudo crear el usuario.",
            "errors": error.detail
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as error:
        return Response({
            "status": "error",
            "message": "Ocurrio un error interno al crear el usuario.",
            "details" : str(error)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": "Datos invalidos.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        email = serializer.validated_data['email']
        password = serializer.validated_data["password"]

        user = AuthService.login(email, password)

        if user is None:
            return Response({
                "status" : "error",
                "message" : "Usuario no creado correctamente."
            }, status=status.HTTP_400_BAD_REQUEST)

        response_serializer = UserSerializer(user)

        return Response({
            "status": "success",
            "message": "Inicio de sesion exitoso."
        }, status=status.HTTP_200_OK)

    except Exception:
        return Response({
            "status": "error",
            "message": "Ocurrio un error interno al iniciar sesion."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --------------------------
# parte de las ventanas
# me , medical profile
# --------------------------
@api_view(["GET","PATCH"])
@permission_classes([AllowAny])
def medical_profile(request):
    email = request.query_params.get('email') or request.data.get('email')
    rut = request.query_params.get('rut') or request.data.get('rut')

    if not email and not rut: # fix, si el email y el rut
        return Response({
            "status" : "error",
            "message" : "Debe enviar email o rut para buscar el perfil medico."
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = UserService.get_user_by_identifier(
            email=email,
            rut=rut,)

        if not UserService.validate_user_exists(user):
            return Response({
                "status": "error",
                "message": "Usuario no encontrado."
            }, status=status.HTTP_404_NOT_FOUND)

        if request.method == "GET":
            profile = UserService.get_medical_profile(user)
            response_serializer = MedicalProfileSerializer(profile)

            return Response({
                "status": "success",
                "message": "Perfil medico obtenido correctamente.",
                "profile": response_serializer.data
            }, status=status.HTTP_200_OK)

        if request.method == "PATCH":
            data = request.data.copy()

            data.pop("email", None)
            data.pop("rut", None)

            serializer = MedicalProfileSerializer(data=data, partial=True)

            if not serializer.is_valid():
                return Response({
                    "status": "error",
                    "message": "Datos invalidos.",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            profile = UserService.update_medical_profile(
                user=user,
                data=serializer.validated_data,
            )

            response_serializer = MedicalProfileSerializer(profile)

            return Response({
                "status": "success",
                "message": "Perfil medico actualizado correctamente.",
                "profile": response_serializer.data
            }, status=status.HTTP_200_OK)

    except Exception:
        return Response({
            "status": "error",
            "message": "Ocurrio un error interno al procesar el perfil medico.",
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ---------------------
# recovery del password
# ---------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_request(request):
    serializer = PasswordResetSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": "Datos invalidos.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        email = serializer.validated_data["email"]

        user = AuthService.request_reset(email)

        if user is None:
            return Response({
                "status": "error",
                "message": "No se pudo iniciar el proceso de recuperacion."
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "success",
            "message": "Usuario encontrado. Puede continuar con el cambio de contrasenha."
        }, status=status.HTTP_200_OK)

    except serializers.ValidationError as error:
        return Response({
            "status": "error",
            "message": "No se pudo iniciar el proceso de recuperacion.",
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    serializer = PasswordResetConfirmSerializer(data=request.data)

    if not serializer.is_valid():
        return Response({
            "status": "error",
            "message": "Datos invalidos.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        email = serializer.validated_data["email"]
        new_password = serializer.validated_data["new_password"]

        user = AuthService.confirm_reset(email, new_password)

        if user is None:
            return Response({
                "status": "error",
                "message": "No se pudo actualizar la contrasenha."
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": "success",
            "message": "Contrasenha actualizada correctamente."
        }, status=status.HTTP_200_OK)

    except serializers.ValidationError as error:
        return Response({
            "status": "error",
            "message": "No se pudo actualizar la contrasenha.",
            "errors": error.detail
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception:
        return Response({
            "status": "error",
            "message": "Ocurrio un error interno al actualizar la contrasenha."
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET"])
@permission_classes([AllowAny])
def me(request):
    email = request.query_params.get("email")
    rut = request.query_params.get("rut")

    if not email and not rut:
        return Response({
            "status": "error",
            "message": "Debe de enviar email o rut para buscar el usuario.",
        }, status=status.HTTP_400_BAD_REQUEST)

    try: # seteamos el valor de none en ambos , al valor propio que nos da el request params
        user = UserService.get_user_by_identifier(email=email, rut=rut)

        if not UserService.validate_user_exists(user):
            return Response({
                "status": "error",
                "message" : "Usuario no encontrado.",
            }, status=status.HTTP_404_NOT_FOUND)

        response_serializer = UserSerializer(user)

        return Response({
            "status": "success",
            "message": "Usuario encontrado correctamente.",
            "user": response_serializer.data
        }, status=status.HTTP_200_OK)

    except Exception:
        return Response({
            "status": "error",
            "message": "Ocurrio un error interno al obtener el usuario.",
        },status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["GET","POST","DELETE"])
@permission_classes([AllowAny])
def profile_image(request):
    email = request.query_params.get("email") or request.data.get("email")
    rut = request.query_params.get("rut") or request.data.get("rut")

    if not email and not rut:
        return Response({
            "status": "error",
            "message" : "Debe de enviar email o rut para buscar el usuario.",
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = UserService.get_user_by_identifier(
            email=email,
            rut=rut,
        )

        if not UserService.validate_user_exists(user):
            return Response({
                "status": "error",
                "message": "Usuario no encontrado."
            }, status=status.HTTP_404_NOT_FOUND)

        if request.method == "GET":
            image = UserService.get_profile_image_metadata(user)

            return Response({
                "status": "success",
                "message": "Imagen de perfil obtenida correctamente.",
                "image": image,
            }, status=status.HTTP_200_OK)

        if request.method == "POST":
            serializer = ProfileImageUploadSerializer(data=request.data)

            if not serializer.is_valid():
                return Response({
                    "status": "error",
                    "message": "Datos invalidos.",
                    "errors": serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)

            file = serializer.validated_data["image"]

            UserService.upload_user_profile_image(
                user=user,
                file=file,
            )

            image = UserService.get_profile_image_metadata(user)

            return Response({
                "status": "success",
                "message": "Imagen de perfil actualizada correctamente.",
                "image": image,
            }, status=status.HTTP_200_OK)

        if request.method == "DELETE":
            UserService.delete_user_profile_image(user)

            return Response({
                "status": "success",
                "message": "Imagen de perfil eliminada correctamente.",
            }, status=status.HTTP_200_OK)

    except serializers.ValidationError as error:
        return Response({
            "status": "error",
            "message": "No se pudo procesar la imagen de perfil.",
            "errors": error.detail,
        }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as error:
        return Response({
            "status": "error",
            "message": "Ocurrio un error interno al procesar la imagen de perfil.",
            "error" : str(error),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)