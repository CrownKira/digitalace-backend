from django_filters import rest_framework as filters

from core.views import BaseAssetAttrViewSet
from core.models import Invoice, Customer, SalesOrder
from customer import serializers


class CustomerFilter(filters.FilterSet):
    class Meta:
        model = Customer
        fields = {
            "last_seen": ["lt", "gt", "lte", "gte", "exact"],
            "agents": ["exact"],
        }


class CustomerViewSet(BaseAssetAttrViewSet):
    """Manage customer in the database"""

    queryset = Customer.objects.all()
    serializer_class = serializers.CustomerSerializer
    filterset_class = CustomerFilter
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
        "receivables",
    ]


class InvoiceViewSet(BaseAssetAttrViewSet):
    """Manage invoice in the database"""

    queryset = Invoice.objects.all()
    serializer_class = serializers.InvoiceSerializer
    search_fields = [
        "id",
        "date",
        "description",
        "payment_date",
        "payment_method",
        "payment_note",
        "grand_total",
        "status",
        "customer__name",
        "salesperson__name",
        "sales_order__id",
    ]


class SalesOrderViewSet(BaseAssetAttrViewSet):
    """Manage customer in the database"""

    queryset = SalesOrder.objects.all()
    serializer_class = serializers.SalesOrderSerializer
    search_fields = [
        "id",
        "date",
        "description",
        "payment_date",
        "payment_method",
        "payment_note",
        "grand_total",
        "status",
        "customer__name",
        "salesperson__name",
    ]
