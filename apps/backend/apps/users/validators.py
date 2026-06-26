import re

from rest_framework import serializers


class UserValidator:

    @staticmethod
    def normalize_email(email):
        
        if not email:
            raise serializers.ValidationError("El email es requerido")

        return email.lower().strip()

    @staticmethod
    def normalize_run(rut):
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

    # Valida que value sea un array JSON basico
    @staticmethod
    def validate_json_list(value, field_name=""):
        if value is None:
            return value
        if not isinstance(value, list):
            raise serializers.ValidationError(
                f"El campo '{field_name}' debe ser un array JSON."
            )
        return value

    # Valida un array de strings con max_length por elemento
    @staticmethod
    def validate_json_list_of_strings(value, field_name="", max_length=100):
        if value is None:
            return value
        if not isinstance(value, list):
            raise serializers.ValidationError(
                f"El campo '{field_name}' debe ser un array JSON."
            )
        for i, item in enumerate(value):
            if not isinstance(item, str):
                raise serializers.ValidationError(
                    f"'{field_name}[{i}]' debe ser un string."
                )
            if len(item) > max_length:
                raise serializers.ValidationError(
                    f"'{field_name}[{i}]' no puede tener más de {max_length} caracteres."
                )
        return value

    # Valida un array de dicts aplicando un schema de reglas (required, max_length, type)
    @staticmethod
    def validate_json_list_of_dicts(value, field_name="", schema=None):
        if value is None:
            return value
        if not isinstance(value, list):
            raise serializers.ValidationError(
                f"El campo '{field_name}' debe ser un array JSON."
            )
        for i, item in enumerate(value):
            if not isinstance(item, dict):
                raise serializers.ValidationError(
                    f"'{field_name}[{i}]' debe ser un objeto JSON."
                )
            if schema:
                for key, rules in schema.items():
                    val = item.get(key)
                    if rules.get("required") and (val is None or val == ""):
                        raise serializers.ValidationError(
                            f"'{field_name}[{i}].{key}' es obligatorio."
                        )
                    if val is not None and isinstance(val, str) and "max_length" in rules:
                        if len(val) > rules["max_length"]:
                            raise serializers.ValidationError(
                                f"'{field_name}[{i}].{key}' no puede tener más de {rules['max_length']} caracteres."
                            )
                    if val is not None and rules.get("type") == "bool" and not isinstance(val, bool):
                        raise serializers.ValidationError(
                            f"'{field_name}[{i}].{key}' debe ser booleano."
                        )
        return value

    # Valida telefono chileno: permite numeros, + y espacios, largo limpio 8-20
    @staticmethod
    def validate_phone_format(phone, field_name="teléfono"):
        if not phone:
            return phone
        if not re.match(r'^[\d+\s]+$', phone):
            raise serializers.ValidationError(
                f"El campo '{field_name}' solo puede contener números, '+' y espacios."
            )
        clean = phone.replace(" ", "").replace("+", "")
        if len(clean) < 8 or len(clean) > 20:
            raise serializers.ValidationError(
                f"El campo '{field_name}' debe tener entre 8 y 20 dígitos."
            )
        return phone

    @staticmethod
    def validate_passwords_match(password, confirm_password):
        if password != confirm_password:
            raise serializers.ValidationError("Las contrasenas no coinciden.")

        return True
