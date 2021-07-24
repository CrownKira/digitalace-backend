from decimal import Decimal
import uuid
import os

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Permission,
)
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _


def get_unique_filename(filename):
    """Get unique filename"""
    ext = filename.split(".")[-1]
    return f"{uuid.uuid4()}.{ext}"


def user_image_file_path(instance, filename):
    """Generate file path for new user image"""
    return os.path.join("uploads/user/images/", get_unique_filename(filename))


def department_image_file_path(instance, filename):
    """Generate file path for new department image"""
    return os.path.join(
        "uploads/department/images/", get_unique_filename(filename)
    )


def role_image_file_path(instance, filename):
    """Generate file path for new role image"""
    return os.path.join("uploads/role/images/", get_unique_filename(filename))


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

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to=department_image_file_path, blank=True)
    company = models.ForeignKey("Company", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Designation(models.Model):
    """Designation in a company"""

    name = models.CharField(max_length=255)
    department = models.ForeignKey("Department", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Role(models.Model):
    """Role in a department"""

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to=role_image_file_path, blank=True)
    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
    )

    def __str__(self):
        return self.name


class Announcement(models.Model):
    """Announcement made"""

    class Status(models.TextChoices):
        DRAFT = "DFT", _("Draft")
        PAID = "OP", _("Open")

    class Severity(models.TextChoices):
        SUCCESS = "SUCC", _("Success")
        INFO = "INFO", _("Info")
        WARNING = "WARN", _("Warning")
        ERROR = "ERR", _("Error")

    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=4,
        blank=True,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    severity = models.CharField(
        max_length=4,
        blank=True,
        choices=Severity.choices,
        default=Severity.INFO,
    )

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        password=None,
        **extra_fields,
    ):
        """Creates and save a new user"""
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            **extra_fields,
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)

        # default objects that come with new users
        UserConfig.objects.create(user=user)

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
        "Company", on_delete=models.SET_NULL, null=True, blank=True
    )
    is_active = models.BooleanField(default=True)
    # is the user an owner of his company?
    # TODO: rename to is_owner
    is_staff = models.BooleanField(default=False)
    email = models.EmailField(max_length=255, unique=True)
    # full name
    name = models.CharField(max_length=255)

    # below are employee fields (null fields for owner)
    # TODO: create a Profile model to store these fields
    designation = models.ForeignKey(
        "Designation", on_delete=models.SET_NULL, null=True, blank=True
    )
    # https://stackoverflow.com/questions/18243039/migrating-manytomanyfield-to-null-true-blank-true-isnt-recognized
    roles = models.ManyToManyField("Role", blank=True)
    # if patch with None, image reference
    # will become empty string (rather than NULL)
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
    phone_no = models.CharField(max_length=255, blank=True)

    date_of_birth = models.DateField(null=True, blank=True)
    date_of_commencement = models.DateField(null=True, blank=True)
    date_of_cessation = models.DateField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"

    def _user_has_role_perm(self, perm, obj):
        return perm in self.get_role_permissions()

    def has_role_perm(self, perm, obj=None):
        """
        Return True if the user has the specified permission. Query all
        available auth backends, but return immediately if any backend returns
        True. Thus, a user who has permission from a single auth backend is
        assumed to have permission in general. If an object is provided, check
        permissions for that object.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        # Otherwise we need to check the backends.
        return self._user_has_role_perm(perm, obj)

    def has_role_perms(self, perm_list, obj=None):
        """
        Return True if the user has each of the specified permissions. If
        object is passed, check if the user has all required perms for it.
        """

        return all(self.has_role_perm(perm, obj) for perm in perm_list)

    def get_role_permissions(self, return_ids=False):
        """Retrieve all the role permissions of the user"""
        perm_list = (
            Permission.objects.all()
            if self.is_staff
            else Permission.objects.filter(
                role__in=self.roles.all()
            ).distinct()
        )
        if return_ids:
            return set(perm.id for perm in perm_list)

        return set("core." + perm.codename for perm in perm_list)

    def __str__(self):
        return self.name


class UserConfig(models.Model):
    """User configuration"""

    class Theme(models.TextChoices):
        LIGHT = "light", _("light")
        DARK = "dark", _("dark")

    class Language(models.TextChoices):
        ENGLISH = "en", _("en")
        MANDARIN = "zh", _("zh")

    user = models.OneToOneField(
        "User",
        on_delete=models.CASCADE,
        # primary_key=True,
    )
    gst_rate = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0.00)
    )
    discount_rate = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0.00)
    )
    theme = models.CharField(
        max_length=255,
        blank=True,
        default=Theme.LIGHT,
        choices=Theme.choices,
    )
    language = models.CharField(
        max_length=255,
        blank=True,
        default=Language.ENGLISH,
        choices=Language.choices,
    )

    def __str__(self):
        return self.user.email

    def delete(self, using=None, keep_parents=False):
        # https://stackoverflow.com/questions/19182001/how-to-protect-objects-from-deletion-in-django
        raise AssertionError(
            "%s object can't be deleted." % (self._meta.object_name,)
        )
