from rest_framework import serializers

from .models import Document, DocumentCategory


class DocumentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentCategory
        fields = ["id", "name", "slug", "icon"]
        read_only_fields = ["id"]


class DocumentSerializer(serializers.ModelSerializer):
    category = DocumentCategorySerializer(read_only=True)
    document_type = serializers.CharField(source="doc_type")
    medical_center = serializers.CharField(source="issuing_institution")
    doctor_name = serializers.CharField(source="issuing_professional")

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "document_type",
            "category",
            "document_date",
            "medical_center",
            "specialty",
            "doctor_name",
            "favorite",
            "bucket_name",
            "file_key",
            "file_url",
            "mime_type",
            "file_size_bytes",
        ]
        read_only_fields = [
            "id",
            "file_key",
            "file_url",
            "mime_type",
            "file_size_bytes",
            "bucket_name"
        ]


class CreateDocumentSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    document_type = serializers.ChoiceField(
        source="doc_type",
        choices=Document.DocType.choices,
        default=Document.DocType.OTHER,
    )
    category_id = serializers.UUIDField(required=False, allow_null=True)
    document_date = serializers.DateField(required=False, allow_null=True)
    medical_center = serializers.CharField(
        source="issuing_institution",
        max_length=255,
        required=False,
        allow_blank=True,
    )
    specialty = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )
    doctor_name = serializers.CharField(
        source="issuing_professional",
        max_length=255,
        required=False,
        allow_blank=True,
    )
    favorite = serializers.BooleanField(default=False)
    file = serializers.FileField()

    def validate_category_id(self, value):
        if value is not None:
            if not DocumentCategory.objects.filter(id=value).exists():
                raise serializers.ValidationError("Categoria no encontrada.")
        return value
