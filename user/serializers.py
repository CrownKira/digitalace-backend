# from company.serializers import PaymentMethodSerializer
# from core.models.transaction import PaymentMethod
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
)


from core.models import UserConfig

# use the following command to easily
# retrieve all fields of User:
# [f.name for f in User._meta.fields]


# TODO: refactor user serializer
class UserSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    """Abstract serialier for user objects"""

    class Meta:
        # https://stackoverflow.com/questions/60238246/why-abstract-true-dosent-inherit-in-meta-class-of-django-model
        # Django does make one adjustment to the Meta class of an abstract base class:
        # before installing the Meta attribute, it sets abstract=False. This means that
        # children of abstract base classes don’t automatically become abstract classes themselves.
        list_serializer_class = BulkListSerializer
        abstract = True

    def get_fields(self):
        fields = super().get_fields()

        # core arguments
        # https://www.django-rest-framework.org/api-guide/fields/#core-arguments
        fields["permissions"] = serializers.SerializerMethodField()
        # qn: why is this field not required when update?
        # TODO: make this required in POST only
        fields["confirm_password"] = serializers.CharField(
            max_length=128, write_only=True
        )

        try:
            if self.context["request"].method in ["POST"]:
                # note that this field will not appear in unittest
                # since the request method is not defined
                fields["confirm_email"] = serializers.EmailField(
                    max_length=255,
                    # write_only is needed since serializer.data will
                    # retrieve all readable fields of this instance
                    # see create() in class CreateOwnerView
                    # specifying write_only here so it will not appear
                    # in serializer.data in response back to the client
                    # set to write_only when you don't want this field to
                    # appear in serializer.data over the course of
                    # creating the object
                    write_only=True,
                )
        except KeyError:
            pass

        return fields

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        # password not required in update
        password = validated_data.pop("password", "")
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

    def validate(self, attrs):
        """Validate and authenticate the user"""
        if self.context["request"].method in ["POST"]:
            email = attrs.get("email")
            confirm_email = attrs.pop("confirm_email")

            if email != confirm_email:
                msg = _("Emails do not match")
                raise serializers.ValidationError(msg)

        password = attrs.get("password", "")
        confirm_password = attrs.pop("confirm_password", "")

        if password and password != confirm_password:
            msg = _("Passwords do not match")
            raise serializers.ValidationError(msg)

        return attrs

    def get_image(self, obj):
        return {
            "src": obj.image.url if obj.image else "",
            "title": obj.image.name if obj.image else "",
        }

    def get_resume(self, obj):
        return {
            "src": obj.resume.url if obj.resume else "",
            "title": obj.resume.name if obj.resume else "",
        }

    def get_permissions(self, obj):
        return obj.get_role_permission(return_ids=True)


# TODO: split create and retrieveupdate
class OwnerProfileSerializer(UserSerializer):
    """
    Serializer for creating, updating and retrieving owner's profile.
    """

    class Meta(UserSerializer.Meta):
        model = get_user_model()
        fields = (
            "id",  # show id to facilitate testing
            "password",
            "is_staff",
            "email",
            "name",
            "image",
            "first_name",
            "last_name",
            "residential_address",
            "postal_code",
            "ic_no",
            "nationality",
            "gender",
            "date_of_birth",
            "phone_no",
        )
        # writable fields will be validated using model
        # validator and added to validated_data
        read_only_fields = (
            "id",
            "is_staff",
            "roles",
            "date_of_commencement",
            "date_of_cessation",
        )
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def get_fields(self):
        fields = super().get_fields()

        try:
            if self.context["request"].method in ["GET"]:
                # read_only=True (w/o overriding) vs override on GET request
                # read_only=True, will override on any request,
                # and it will be read_only regardless of the http method
                # override on GET request, will only override on GET request
                fields["image"] = serializers.SerializerMethodField()
                fields["company_name"] = serializers.SerializerMethodField()
            else:
                fields["company_name"] = serializers.CharField(
                    max_length=255,
                    write_only=True,
                )
            if self.context["request"].method in ["PUT, PATCH"]:
                fields["image"] = serializers.ImageField(allow_null=True)
        except KeyError:
            pass

        return fields

    def get_company_name(self, obj):
        return obj.company.name if obj.company else ""

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        # None: not given (prefer this)
        # "": not given but save as empty string
        company_name = validated_data.pop("company_name", None)
        user = super().update(instance, validated_data)

        if user.is_staff and company_name:  # company_name can't be blank
            company = user.company
            company.name = company_name
            company.save(update_fields=["name"])

        return user


class EmployeeProfileSerializer(UserSerializer):
    """
    Serializer for updating and retrieving employee's profile.
    """

    class Meta(UserSerializer.Meta):
        model = get_user_model()
        fields = (
            "id",
            "password",
            "is_staff",
            "email",
            "name",
            "roles",
            "image",
            "resume",
            "first_name",
            "last_name",
            "residential_address",
            "postal_code",
            "ic_no",
            "nationality",
            "gender",
            "date_of_birth",
            "date_of_commencement",
            "date_of_cessation",
            "phone_no",
            "designation",
        )
        read_only_fields = (
            "id",
            "is_staff",
            "roles",
            "date_of_commencement",
            "date_of_cessation",
        )
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def get_fields(self):
        fields = super().get_fields()

        fields["department"] = serializers.SerializerMethodField(
            read_only=True
        )

        try:
            if self.context["request"].method in ["GET"]:
                fields["image"] = serializers.SerializerMethodField()
            else:
                fields["image"] = serializers.ImageField(allow_null=True)
        except KeyError:
            pass

        return fields

    def get_department(self, obj):
        return (
            (
                obj.designation.department.pk
                if obj.designation.department
                else None
            )
            if obj.designation
            else None
        )


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""

    email = serializers.CharField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials")
            raise serializers.ValidationError(msg, code="authentication")

        attrs["user"] = user
        return attrs
