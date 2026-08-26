from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


def current_tos_version():
    return settings.TOS_CONSENT_VERSION


def current_data_consent():
    return settings.SENSITIVE_DATA_CONSENT_VERSION


# Create your models here.
class UserManager(BaseUserManager):
    @classmethod
    def normalize_email(cls, email):
        email = email or ""
        try:
            email_name, domain_part = email.strip().rsplit("@", 1)
        except ValueError:
            pass
        else:
            email = email_name + "@" + domain_part
        return email.lower()

    def _create_user_object(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)

        return user

    def _create_user(self, email, password, **extra_fields):
        user = self._create_user_object(email, password, **extra_fields)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    date_joined = models.DateTimeField(default=timezone.now)

    tos_accepted = models.BooleanField(default=False)
    tos_accepted_date = models.DateTimeField(default=timezone.now)
    tos_version = models.IntegerField(default=current_tos_version)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email


class Profile(models.Model):
    class GoalChoices(models.TextChoices):
        LOSE_WEIGHT = "diet", "Abnehmen"
        MAINTAIN_WEIGHT = "maintain", "Gewicht halten"
        GAIN_WEIGHT = "gain", "Zunehmen"

    class SexChoices(models.TextChoices):
        MALE = (
            "male",
            "Männlich",
        )
        FEMALE = "female", "Weiblich"

    username = models.CharField(
        unique=True,
        max_length=32,
        blank=True,
        null=True,
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    sex = models.CharField(
        choices=SexChoices,
        max_length=6,
        blank=True,
        null=True,
    )

    height = models.IntegerField(
        blank=True,
        null=True,
    )

    weight = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
    )

    target_calories = models.IntegerField(
        blank=True,
        null=True,
    )

    target_fat = models.IntegerField(
        blank=True,
        null=True,
    )

    target_protein = models.IntegerField(
        blank=True,
        null=True,
    )

    target_carbs = models.IntegerField(
        blank=True,
        null=True,
    )

    goal = models.CharField(
        choices=GoalChoices,
        blank=True,
        null=True,
        max_length=15,
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True,
    )

    data_consent = models.BooleanField(default=False)
    data_consent_date_granted = models.DateTimeField(blank=True, null=True)
    data_consent_date_revoked = models.DateTimeField(blank=True, null=True)
    data_consent_version = models.IntegerField(default=current_data_consent)

    def __str__(self):
        if self.username:
            return self.username

        return str(self.user)
