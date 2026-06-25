import re

from rest_framework import serializers


class UserValidator:
    # ------------------------------------------
    # normalizadores de email y rut
    # ------------------------------------------
    @staticmethod
    def normalize_email(email):
        # valida que el correo no venga vacio
        if not email:
            raise serializers.ValidationError("El email es requerido")

        # elimina espacios al inicio/final y deja el correo en minusculas
        return email.lower().strip()

    @staticmethod
    def normalize_run(rut):
        # valida que el rut no venga vacio
        if not rut:
            raise serializers.ValidationError("El rut es requerido")

        # elimina espacios y deja la k en mayuscula
        rut = rut.strip().upper()

        # rechazar puntos
        if "." in rut:
            raise serializers.ValidationError(
                "El RUT no debe contener puntos."
            )

        # exigir exactamente un guion
        if rut.count("-") != 1:
            raise serializers.ValidationError(
                "El RUT debe incluir un guion (ej: 12345678-9)."
            )

        return rut

    # ------------------------
    # validadores de logica
    # ------------------------
    @staticmethod
    def validate_email_format(email):
        # primero normalizamos el correo para trabajar siempre con el mismo formato
        email = UserValidator.normalize_email(email)

        # valida que el correo contenga @
        if "@" not in email:
            raise serializers.ValidationError("El correo debe de contener un @.")

        # split("@") separa el correo en partes
        # [-1] toma la ultima parte, que corresponde al dominio
        domain = email.split("@")[-1]

        # valida que el dominio tenga al menos un punto
        # ejemplo valido: gmail.com
        if "." not in domain:
            raise serializers.ValidationError("El correo debe de contener un dominio valido.")

        return email

    @staticmethod
    def validate_rut_format(rut):
        # normalizar rut manteniendo guion
        rut = UserValidator.normalize_run(rut)

        # separar cuerpo y digito verificador por guion
        body, verifier = rut.split("-")

        # validar largo del cuerpo (7 a 8 digitos)
        if len(body) < 7 or len(body) > 8:
            raise serializers.ValidationError(
                "El cuerpo del RUT debe tener entre 7 y 8 digitos."
            )

        if not body.isdigit():
            raise serializers.ValidationError("El cuerpo del RUT debe contener solo numeros.")

        if len(verifier) != 1:
            raise serializers.ValidationError("El digito verificador debe ser un solo caracter.")

        if not verifier.isdigit() and verifier != "K":
            raise serializers.ValidationError("El digito verificador debe ser un numero o K.")

        # validar digito verificador con algoritmo modulo 11
        # secuencia de multiplicadores: 2, 3, 4, 5, 6, 7, 2, 3...
        # se aplica desde el ultimo digito del cuerpo hacia el primero
        total = 0
        multiplier = 2
        for digit in reversed(body):
            total += int(digit) * multiplier
            multiplier = multiplier + 1 if multiplier < 7 else 2
        remainder = total % 11
        # resultado 11 equivale a dv "0", resultado 10 equivale a dv "K"
        result = 11 - remainder
        if result == 11:
            expected = "0"
        elif result == 10:
            expected = "K"
        else:
            expected = str(result)

        if verifier != expected:
            raise serializers.ValidationError(
                f"El digito verificador no es valido. Deberia ser {expected}."
            )

        return rut

    @staticmethod
    def validate_password_strength(password):
        # valida que la contrasena no venga vacia
        if not password:
            raise serializers.ValidationError("La contrasena es obligatoria.")

        # valida largo minimo
        if len(password) < 6:
            raise serializers.ValidationError("La contrasena debe tener al menos 6 caracteres.")

        # valida largo maximo
        if len(password) > 12:
            raise serializers.ValidationError("La contrasena no puede tener mas de 12 caracteres.")

        # re.search busca si existe al menos una coincidencia con el patron indicado
        # [A-Z] valida que exista al menos una mayuscula
        if not re.search(r"[A-Z]", password):
            raise serializers.ValidationError("La contrasena debe tener al menos una mayuscula.")

        # [a-z] valida que exista al menos una minuscula
        if not re.search(r"[a-z]", password):
            raise serializers.ValidationError("La contrasena debe tener al menos una minuscula.")

        # \d valida que exista al menos un numero
        if not re.search(r"\d", password):
            raise serializers.ValidationError("La contrasena debe tener al menos un numero.")

        # [^\w\s] valida que exista al menos un signo o simbolo
        # es decir, algo que no sea letra, numero, guion bajo o espacio
        if not re.search(r"[^\w\s]", password):
            raise serializers.ValidationError("La contrasena debe tener al menos un signo o simbolo.")

        return password

    @staticmethod
    def validate_passwords_match(password, confirm_password):
        # valida que ambas contrasenas sean iguales
        if password != confirm_password:
            raise serializers.ValidationError("Las contrasenas no coinciden.")

        return True
