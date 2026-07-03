import uuid

from django.conf import settings
from django.db import models


# categoria de documentos (examen, receta, vacuna, etc)
class DocumentCategory(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)

    icon = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    class Meta:
        db_table = "document_categories"
        managed = False  # tabla administrada manualmente desde schema.sql

    def __str__(self):
        return self.name


# documento medico subido por el usuario
class Document(models.Model):
    # tipos de documento disponibles
    class DocType(models.TextChoices):
        EXAM = "exam", "Exam"
        PRESCRIPTION = "prescription", "Prescription"
        SICK_LEAVE = "sick_leave", "Sick leave"
        REPORT = "report", "Report"
        VACCINE = "vaccine", "Vaccine"
        OTHER = "other", "Other"
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # relacion con el usuario dueño del documento
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        related_name="documents",
        db_column="user_id"
    )

    # relacion con la categoria del documento
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="documents",
        db_column="category_id"
    )

    title = models.CharField(max_length=255)

    doc_type = models.CharField(
        max_length=30,
        choices=DocType.choices,
        default=DocType.OTHER
    )

    file_key = models.CharField(max_length=500)  # ruta del archivo en supabase storage

    file_url = models.TextField(
        null=True,
        blank=True
    )

    mime_type = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    file_size_bytes = models.IntegerField(
        null=True,
        blank=True
    )

    document_date = models.DateField(
        null=True,
        blank=True
    )

    issuing_institution = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    issuing_professional = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    specialty = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    favorite = models.BooleanField(default=False)

    bucket_name = models.CharField(
        max_length=150,
        null=True,
        blank=True
    )

    extracted_text = models.TextField(
        null=True,
        blank=True
    )

    # metadatos generados por analisis de ia
    ai_metadata = models.JSONField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # fecha de eliminacion logica (soft delete)
    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:
        db_table = "documents"
        managed = False  # tabla administrada manualmente desde schema.sql

    def __str__(self):
        return self.title