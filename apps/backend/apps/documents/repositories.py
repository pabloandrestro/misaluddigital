from django.utils import timezone

from .models import Document, DocumentCategory


class DocumentRepository:

    @staticmethod
    def get_all_by_user(user):
        return Document.objects.filter(
            user=user,
            deleted_at__isnull=True
        )

    @staticmethod
    def get_by_id(document_id):
        return Document.objects.filter(
            id=document_id,
            deleted_at__isnull=True
        ).first()

    @staticmethod
    def create_document(data):
        document = Document.objects.create(**data)

        return document

    @staticmethod
    def save_document(document):
        document.save()

        return document

    @staticmethod
    def soft_delete(document):
        document.deleted_at = timezone.now()
        document.save()

        return document


    # metodo faltante
    @staticmethod
    def get_by_id_and_user(document_id, user):
        return Document.objects.filter(
            id=document_id,
            user=user,
            deleted_at__isnull=True
        ).first()

    # implementar cuando se requiera distincion entre activo y eliminado
    @staticmethod
    def get_active_by_id_and_user(document_id, user):
        return Document.objects.filter(
            id=document_id,
            user=user,
            deleted_at__isnull=True
        ).first()


class DocumentCategoryRepository:

    @staticmethod
    def get_all():
        return DocumentCategory.objects.all()

    @staticmethod
    def get_by_id(category_id):
        return DocumentCategory.objects.filter(
            id=category_id
        ).first()