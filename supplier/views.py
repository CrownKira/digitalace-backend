from core.pagination import CustomPagination
from core.views import BaseClassAttrForViewSet

from core.models import Receive, Supplier

from supplier import serializers


class ReceiveViewSet(BaseClassAttrForViewSet):
    """Manage Receive in the database"""
    queryset = Receive.objects.all()
    serializer_class = serializers.ReceiveSerializer
    pagination_class = CustomPagination


class SupplierViewSet(BaseClassAttrForViewSet):
    """Manage Supplier in the database"""
    queryset = Supplier.objects.all()
    serializer_class = serializers.SupplierSerializer
    pagination_class = CustomPagination
