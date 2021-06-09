from django_filters import rest_framework as filters

from core.views import BaseAssetAttrViewSet
from core.models import Receive, Supplier, PurchaseOrder
from supplier import serializers


class SupplierFilter(filters.FilterSet):
    class Meta:
        model = Supplier
        fields = {
            "last_seen": ["lt", "gt", "lte", "gte", "exact"],
        }


class SupplierViewSet(BaseAssetAttrViewSet):
    """Manage Supplier in the database"""

    queryset = Supplier.objects.all()
    serializer_class = serializers.SupplierSerializer
    filterset_class = SupplierFilter
    search_fields = [
        "attention",
        "name",
        "address",
        "city",
        "state",
        "zipcode",
        "contact",
        "term",
        "phone_no",
        "email",
        "payables",
    ]


class ReceiveViewSet(BaseAssetAttrViewSet):
    """Manage Receive in the database"""

    queryset = Receive.objects.all()
    serializer_class = serializers.ReceiveSerializer
    search_fields = [
        "id",
        "date",
        "description",
        "payment_date",
        "payment_method",
        "payment_note",
        "grand_total",
        "status",
        "supplier__name",
        "purchase_order__id",
    ]


class PurchaseOrderViewSet(BaseAssetAttrViewSet):
    """Manage Supplier in the database"""

    queryset = PurchaseOrder.objects.all()
    serializer_class = serializers.PurchaseOrderSerializer
    search_fields = [
        "id",
        "date",
        "description",
        "payment_date",
        "payment_method",
        "payment_note",
        "grand_total",
        "status",
        "supplier__name",
    ]
