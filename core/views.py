from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_bulk import BulkModelViewSet


from core.utils import validate_bulk_reference_uniqueness
from .pagination import StandardResultsSetPagination


class BaseAttrViewSet(
    # ListBulkCreateUpdateDestroyAPIView, viewsets.ModelViewSet
    BulkModelViewSet
):
    """Base attr viewset for all viewsets"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination
    ordering_fields = "__all__"
    ordering = ["-id"]

    def allow_bulk_destroy(self, qs, filtered):
        """Don't forget to fine-grain this method"""
        # TODO: write implementation for bulk destroy
        return False


class BaseAssetAttrViewSet(BaseAttrViewSet):
    """Base attr viewset for company asset viewsets"""

    def get_queryset(self):
        company = self.request.user.company
        return self.queryset.filter(company=company).distinct()

    def perform_create(self, serializer):
        company = self.request.user.company
        serializer.save(company=company)


class BaseDocumentViewSet(BaseAssetAttrViewSet):
    """Base viewset for documents"""

    def perform_bulk_create(self, serializer):
        validate_bulk_reference_uniqueness(serializer.validated_data)
        return self.perform_create(serializer)

    def perform_bulk_update(self, serializer):
        validate_bulk_reference_uniqueness(serializer.validated_data)
        return self.perform_update(serializer)

    def perform_create(self, serializer):
        company = self.request.user.company
        serializer.save(
            company=company,
            # **self._get_calculated_fields(serializer)
        )

    # def perform_update(self, serializer):
    #     serializer.save(**self._get_calculated_fields(serializer))
