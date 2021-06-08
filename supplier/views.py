from core.views import BaseAssetAttrViewSet
from core.models import Receive, Supplier, PurchaseOrder

from supplier import serializers


class SupplierViewSet(BaseAssetAttrViewSet):
    """Manage Supplier in the database"""

    queryset = Supplier.objects.all()
    serializer_class = serializers.SupplierSerializer


class ReceiveViewSet(BaseAssetAttrViewSet):
    """Manage Receive in the database"""

    queryset = Receive.objects.all()
    serializer_class = serializers.ReceiveSerializer


class PurchaseOrderViewSet(BaseAssetAttrViewSet):
    """Manage Supplier in the database"""

    queryset = PurchaseOrder.objects.all()
    serializer_class = serializers.PurchaseOrderSerializer
