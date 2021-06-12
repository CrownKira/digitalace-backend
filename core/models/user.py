from decimal import Decimal
import uuid
import os

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Permission
)
from django.core.validators import FileExtensionValidator
from django.db.models.fields import CharField
from django.utils.translation import gettext_lazy as _


def get_unique_filename(filename):
    """Get unique filename"""
    ext = filename.split(".")[-1]
    return f"{uuid.uuid4()}.{ext}"


def user_image_file_path(instance, filename):
    """Generate file path for new user image"""
    return os.path.join("uploads/user/images/", get_unique_filename(filename))


def user_resume_file_path(instance, filename):
    """Generate file path for new user resume"""
    return os.path.join("uploads/user/resumes/", get_unique_filename(filename))


class Company(models.Model):
    """Company that a user belongs to"""

    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    website_url = models.URLField(blank=True)
    tel_no = models.CharField(max_length=255, blank=True)
    fax_no = models.CharField(max_length=255, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=255, blank=True)
    # TODO: consider django_countries
    # https://stackoverflow.com/questions/2963930/django-country-drop-down-list
    country = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name


class Department(models.Model):
    """Department in a company"""

    name = CharField(max_length=255)
    company = models.ForeignKey("Company", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Role(models.Model):
    """Role in a department"""

    # TODO: rename to designation

    name = CharField(max_length=255)
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
    )
    # department = models.ForeignKey("Department", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Creates and save a new user"""
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""

    class Gender(models.TextChoices):
        MALE = "M", _("Male")
        FEMALE = "F", _("Female")

    # null=True since superuser does not have a company
    # if company is null, disable all functionalities
    # can be blank (if created from admin page)
    company = models.ForeignKey(
        "Company", on_delete=models.CASCADE, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    # is the user an owner of his company?
    # TODO: rename to is_owner
    is_staff = models.BooleanField(default=False)
    email = models.EmailField(max_length=255, unique=True)
    # full name
    name = models.CharField(max_length=255)

    # below are employee fields (null fields for owner)
    department = models.ForeignKey(
        "Department", on_delete=models.CASCADE, null=True, blank=True
    )
    role = models.ForeignKey(
        "Role", on_delete=models.CASCADE, null=True, blank=True
    )

    image = models.ImageField(upload_to=user_image_file_path, blank=True)
    resume = models.FileField(
        upload_to=user_resume_file_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "png", "jpeg", "jpg", "txt"]
            )
        ],
        blank=True,
    )

    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    residential_address = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=255, blank=True)
    ic_no = models.CharField(max_length=255, blank=True)
    nationality = models.CharField(max_length=255, blank=True)
    gender = models.CharField(
        max_length=1,
        blank=True,
        choices=Gender.choices,
    )

    date_of_birth = models.DateField(null=True, blank=True)
    date_of_commencement = models.DateField(null=True, blank=True)
    date_of_cessation = models.DateField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def has_role_perms(self, perm_list):
        """checks for perm"""
        return all(perm in self.role.permissions for perm in perm_list)

    def __str__(self):
        return self.name


class UserConfig(models.Model):
    """User configuration"""

    user = models.OneToOneField(
        "User",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    gst_rate = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0.00)
    )
    discount_rate = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0.00)
    )
    theme = models.CharField(max_length=255, blank=True, default="light")
    language = models.CharField(max_length=255, blank=True, default="en")

    def __str__(self):
        return self.user.name
