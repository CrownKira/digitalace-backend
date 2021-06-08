from rest_framework import viewsets, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class BaseAssetAttrViewSet(viewsets.ModelViewSet):
    """Base attr for viewsets"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    filter_backends = [filters.OrderingFilter]
    ordering_fields = "__all__"
    ordering = ["-id"]

    def get_queryset(self):
        company = self.request.user.company
        return self.queryset.filter(company=company)
