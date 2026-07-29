from django.conf import settings
from rest_framework import serializers
from supabase import create_client


# centraliza lectura de credenciales y creacion del cliente supabase,
# compartido entre apps.users y apps.documents
def get_supabase_client(error_message):
    supabase_url = getattr(settings, "SUPABASE_URL", "")
    supabase_key = getattr(settings, "SUPABASE_SERVICE_KEY", "")

    if not supabase_url or not supabase_key:
        raise serializers.ValidationError(error_message)

    return create_client(supabase_url, supabase_key)
