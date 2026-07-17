from django.utils import timezone
from .models import TemporaryAccessLink


class TemporaryAccessLinkRepository:

    # crea y retorna un nuevo enlace de acceso temporal
    @staticmethod
    def create(data):
        return TemporaryAccessLink.objects.create(**data)

    # busca un enlace por token sin validar expiracion
    @staticmethod
    def get_by_token(token):
        return TemporaryAccessLink.objects.filter(token=token).first()

    # busca un enlace activo por token validando que no este expirado
    @staticmethod
    def get_active_by_token(token):
        return TemporaryAccessLink.objects.filter(
            token=token,
            expires_at__gt=timezone.now()
        ).first()

    # guarda los cambios de un enlace en la base de datos
    @staticmethod
    def save(link):
        link.save()
        return link
