from django.utils.translation import ugettext_lazy as _

from rest_framework import (
    generics,
    authentication,
    permissions,
    status,
    serializers,
)
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response

from user.serializers import UserSerializer, AuthTokenSerializer
from core.models import Company


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        user = serializer.instance
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "id": user.id,
                "fullName": user.name,
                "avatar": user.image.url if user.image else "",
                "permissions": user.get_group_permissions(),
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        # validate confirm fields here since serializer.validate()
        # is shared between create and update
        email = serializer.validated_data.get("email", None)
        password = serializer.validated_data.get("password", None)

        confirm_email = serializer.initial_data.get("confirm_email", None)
        confirm_password = serializer.initial_data.get(
            "confirm_password", None
        )

        if email != confirm_email:
            msg = _("Emails do not match")
            raise serializers.ValidationError(msg)

        if password != confirm_password:
            msg = _("Passwords do not match")
            raise serializers.ValidationError(msg)

        company = Company.objects.create(
            name=serializer.initial_data.get("company", "")
        )
        serializer.save(is_staff=True, company=company)


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "id": user.id,
                "fullName": user.name,
                "avatar": user.image.url if user.image else "",
                "permissions": user.get_group_permissions(),
            }
        )


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""

    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user

    def update(self, request, *args, **kwargs):
        print("hello")
        print(request.data)
        return super().update(request, *args, **kwargs)
