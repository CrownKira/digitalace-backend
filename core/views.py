from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# from rest_framework.pagination import PageNumberPagination
from .pagination import StandardResultsSetPagination


class BaseAttrViewSet(viewsets.ModelViewSet):
    """Base attr viewset for all viewsets"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination
    ordering_fields = "__all__"
    ordering = ["-id"]


class BaseAssetAttrViewSet(BaseAttrViewSet):
    """Base attr viewset for company asset viewsets"""

    def get_queryset(self):
        company = self.request.user.company
        return self.queryset.filter(company=company).distinct()

    def perform_create(self, serializer):
        company = self.request.user.company
        serializer.save(company=company)
