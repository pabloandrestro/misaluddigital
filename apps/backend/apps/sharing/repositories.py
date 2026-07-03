from .models import TemporaryAccessLink


class TemporaryAccessLinkRepository:

    # todo: implementar creacion de enlace de acceso temporal
    @staticmethod
    def create(data):
        pass

    # todo: implementar busqueda por token sin validar expiracion
    @staticmethod
    def get_by_token(token):
        pass

    # todo: implementar busqueda por token validando que no haya expirado
    @staticmethod
    def get_active_by_token(token):
        pass

    # todo: implementar persistencia del enlace
    @staticmethod
    def save(link):
        pass
