from django_filters import rest_framework as filters

from core.views import BaseAssetAttrViewSet, BaseDocumentViewSet
from core.models import Receive, Supplier, PurchaseOrder
from core.utils import validate_bulk_reference_uniqueness
from customer.serializers import _update_inventory
from supplier import serializers


class SupplierFilter(filters.FilterSet):
    class Meta:
        model = Supplier
        fields = {
            "reference": ["exact"],
            "name": ["icontains"],
            "last_seen": ["lt", "gt", "lte", "gte", "exact"],
        }


class SupplierViewSet(BaseAssetAttrViewSet):
    """Manage Supplier in the database"""

    queryset = Supplier.objects.all()
    serializer_class = serializers.SupplierSerializer
    filterset_class = SupplierFilter
    search_fields = [
        "name",
        "attention",
        "email",
        "phone_no",
        "payables",
    ]

    def perform_bulk_create(self, serializer):
        validate_bulk_reference_uniqueness(serializer.validated_data)
        return self.perform_create(serializer)

    def perform_bulk_update(self, serializer):
        validate_bulk_reference_uniqueness(serializer.validated_data)
        return self.perform_update(serializer)


class ReceiveFilter(filters.FilterSet):
    class Meta:
        model = Receive
        fields = {
            "reference": ["icontains", "exact"],
            "date": ["gte", "lte"],
            "status": ["exact"],
        }


class ReceiveViewSet(BaseDocumentViewSet):
    """Manage Receive in the database"""

    queryset = Receive.objects.all()
    serializer_class = serializers.ReceiveSerializer
    filterset_class = ReceiveFilter
    search_fields = [
        "reference",
        "date",
        "supplier__name",
        "supplier__address",
        "purchase_order__reference",
        "status",
        "grand_total",
    ]

    def perform_destroy(self, instance):
        for item in instance.creditnoteitem_set:
            _update_inventory(
                instance.status,
                item.product,
                item.quantity,
                adjust_up=False,
                affect_sales=False,
            )
        instance.delete()


class PurchaseOrderFilter(filters.FilterSet):
    class Meta:
        model = PurchaseOrder
        fields = {
            "reference": ["icontains", "exact"],
            "date": ["gte", "lte"],
            "status": ["exact"],
        }


class PurchaseOrderViewSet(BaseDocumentViewSet):
    """Manage Supplier in the database"""

    queryset = PurchaseOrder.objects.all()
    serializer_class = serializers.PurchaseOrderSerializer

    filterset_class = PurchaseOrderFilter
    search_fields = [
        "reference",
        "date",
        "supplier__name",
        "supplier__address",
        "receive__reference",
        "status",
        "grand_total",
    ]
