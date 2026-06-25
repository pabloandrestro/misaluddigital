from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
import uuid


# manager personalizado para crear usuarios usando email en vez de username
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra):
        if not email:
            raise ValueError("El correo es obligatorio")
        email = self.normalize_email(email)
        user  = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra)


# usuario del sistema, login con email en vez de username
# tabla administrada por django (managed=True por defecto)
class User(AbstractBaseUser, PermissionsMixin):
    id             = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email          = models.EmailField(unique=True)
    rut            = models.CharField(max_length=12, unique=True, null=True, blank=True)  # rut chileno del usuario
    name           = models.CharField(max_length=60, blank=True, default="")
    is_active      = models.BooleanField(default=True)
    is_staff       = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)  # indica si el correo ya fue verificado
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    objects  = UserManager()
    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"


    def __str__(self):
        return self.email


# perfil medico del usuario, datos personales y de salud
class MedicalProfile(models.Model):
    BLOOD_TYPES = [("A+","A+"),("A-","A-"),("B+","B+"),("B-","B-"),
                   ("AB+","AB+"),("AB-","AB-"),("O+","O+"),("O-","O-")]  # tipos de sangre disponibles

    user                   = models.OneToOneField(User, on_delete=models.CASCADE, related_name="medical_profile")  # relacion con el usuario dueño del perfil
    first_name             = models.CharField(max_length=48)
    last_name              = models.CharField(max_length=48)
    birthdate              = models.DateField(null=True, blank=True)
    genre                  = models.CharField(max_length=20, blank=True)
    blood_type             = models.CharField(max_length=3, choices=BLOOD_TYPES, blank=True)
    weight                 = models.IntegerField(null=True, blank=True)
    height                 = models.IntegerField(null=True, blank=True)
    profile_image          = models.URLField(blank=True)
    allergies              = models.TextField(blank=True)
    chronic_conditions     = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone= models.CharField(max_length=20, blank=True)
    updated_at             = models.DateTimeField(auto_now=True)
    address                = models.CharField(max_length=255, blank=True)
    relevance_type         = models.CharField(max_length=100, blank=True)
    current_medications    = models.TextField(blank=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True)
    recent_medical_history = models.TextField(blank=True)

    class Meta:
        db_table = "medical_profiles"


    def __str__(self):
        return f"{self.first_name} {self.last_name}"
