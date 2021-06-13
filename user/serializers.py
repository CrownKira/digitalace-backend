from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the users object"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            if self.context["request"].method in ["GET"]:
                self.fields["image"] = serializers.SerializerMethodField()
                self.fields["resume"] = serializers.SerializerMethodField()
        except KeyError:
            pass

    class Meta:
        model = get_user_model()
        # use the following command to easily
        # retrieve all fields of User:
        # [f.name for f in User._meta.fields]
        fields = (
            "id",
            "password",
            # "last_login",
            # "is_superuser",
            # "company",
            # "is_active",
            # "is_staff",
            "email",
            "name",
            "department",
            "role",
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
        )
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    # TODO: create employee by POST /employees/
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
        if self.context["request"].method in ["POST"]:
            email = attrs.get("email", None)
            confirm_email = self.initial_data.get("confirm_email", None)

            if email != confirm_email:
                msg = _("Emails do not match")
                raise serializers.ValidationError(msg)

            attrs["company"] = self.initial_data.get("company", "")

        password = attrs.get("password", None)
        confirm_password = self.initial_data.get("confirm_password", None)

        if password != confirm_password:
            msg = _("Passwords do not match")
            raise serializers.ValidationError(msg)

        return attrs

    def get_image(self, obj):
        return obj.image.url if obj.image else ""

    def get_resume(self, obj):
        return obj.resume.url if obj.resume else ""


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
