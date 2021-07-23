from django.shortcuts import get_object_or_404

from rest_framework import (
    generics,
    authentication,
    permissions,
    status,
)
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response

from core.permissions import RolePermission
from core.models import Company, UserConfig
from user.serializers import (
    OwnerProfileSerializer,
    EmployeeProfileSerializer,
    AuthTokenSerializer,
)
from company.serializers import UserConfigSerializer


# TODO: refactor owner and employee views and serializer
class CreateOwnerView(generics.CreateAPIView):
    """Create a new company and owner in the system"""

    serializer_class = OwnerProfileSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        user = serializer.instance
        token, created = Token.objects.get_or_create(user=user)
        # serializer.data will serialize all the readable fields
        return Response(
            {
                **serializer.data,
                "token": token.key,
            },
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        company = Company.objects.create(
            name=serializer.validated_data.pop("company_name")
        )
        serializer.save(is_staff=True, company=company)


class ManageProfileView(generics.RetrieveUpdateAPIView):
    """View for retrieving and updating user profile"""

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.
        You may want to override this if you need to provide different
        serializations depending on the incoming request.
        (Eg. admins get full serialization, others get basic serialization)
        """
        return (
            OwnerProfileSerializer
            if self.request.user.is_staff
            else EmployeeProfileSerializer
        )


class UserConfigView(generics.RetrieveUpdateAPIView):
    """View for retrieving and updating user config"""

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserConfigSerializer

    def get_object(self):
        queryset = UserConfig.objects.all()
        userconfig = get_object_or_404(queryset, user=self.request.user)
        return userconfig


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})
