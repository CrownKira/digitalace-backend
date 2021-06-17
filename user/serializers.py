from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

# use the following command to easily
# retrieve all fields of User:
# [f.name for f in User._meta.fields]


class UserSerializer(serializers.ModelSerializer):
    """Abstract serialier for user objects"""

    permissions = serializers.SerializerMethodField()

    class Meta:
        abstract = True

    def get_fields(self):
        fields = super().get_fields()
        if self.context["request"].method in ["GET"]:
            fields["image"] = serializers.SerializerMethodField()
        else:
            fields["image"] = serializers.ImageField(allow_null=True)
        return fields

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user

    def validate(self, attrs):
        """Validate and authenticate the user"""

        # TODO: create a function to abstract away confirm logic
        if self.context["request"].method in ["POST"]:
            email = attrs.get("email")
            # TODO: assign a field to all self.initial_data
            # TODO: make this a required field
            confirm_email = self.initial_data.get("confirm_email")

            if email != confirm_email:
                msg = _("Emails do not match")
                raise serializers.ValidationError(msg)

            attrs["company"] = self.initial_data.get("company", "")

        password = attrs.get("password")
        confirm_password = self.initial_data.get("confirm_password")

        if password != confirm_password:
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
        return obj.get_role_permissions()


class OwnerProfileSerializer(UserSerializer):
    """
    Serializer for creating, updating and retrieving owner's profile.
    """

    company_name = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "password",
            # "last_login",
            # "is_superuser",
            "company_name",
            # "is_active",
            "is_staff",
            "email",
            "name",
            # "department",
            # "roles",
            "image",
            # "resume",
            "first_name",
            "last_name",
            "residential_address",
            "postal_code",
            "ic_no",
            "nationality",
            "gender",
            "date_of_birth",
            # "date_of_commencement",
            # "date_of_cessation",
            "phone_no",
            "permissions",
        )
        # writable fields will be validated using model
        # validator and added to validated_data
        read_only_fields = (
            "id",
            "is_staff",
            "department",
            "roles",
            "date_of_commencement",
            "date_of_cessation",
            "resume",
        )
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def get_company_name(self, obj):
        return obj.company.name if obj.company else ""

    def validate(self, attrs):
        """Validate and authenticate the user"""

        super_attrs = super().validate(attrs)

        if self.context["request"].method in ["PUT", "PATCH"]:
            # TODO: make this a required field
            # hint: need to assign a field to this
            # to get validated (eg. CharField)
            super_attrs["company_name"] = self.initial_data.get(
                "company_name", ""
            )

        return super_attrs

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        company_name = validated_data.pop("company_name")
        user = super().update(instance, validated_data)

        if user.is_staff:
            company = user.company
            company.name = company_name
            company.save(update_fields=["name"])

        return user


class EmployeeProfileSerializer(UserSerializer):
    """
    Serializer for updating and retrieving employee's profile.
    """

    company_name = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "password",
            # "last_login",
            # "is_superuser",
            "company_name",
            # "is_active",
            "is_staff",
            "email",
            "name",
            "department",
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
            "permissions",
        )
        read_only_fields = (
            "id",
            "is_staff",
            "department",
            "roles",
            "date_of_commencement",
            "date_of_cessation",
            "resume",
        )
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def get_fields(self):
        fields = super().get_fields()
        if self.context["request"].method in ["GET"]:
            fields["resume"] = serializers.SerializerMethodField()
        return fields

    def get_company_name(self, obj):
        return obj.company.name if obj.company else ""


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
