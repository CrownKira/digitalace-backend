from core.views import BaseAssetAttrViewSet

from core.models import Invoice, Customer, SalesOrder

from customer import serializers


class InvoiceViewSet(BaseAssetAttrViewSet):
    """Manage invoice in the database"""

    queryset = Invoice.objects.all()
    serializer_class = serializers.InvoiceSerializer


class SalesOrderViewSet(BaseAssetAttrViewSet):
    """Manage customer in the database"""

    queryset = SalesOrder.objects.all()
    serializer_class = serializers.SalesOrderSerializer


class CustomerViewSet(BaseAssetAttrViewSet):
    """Manage customer in the database"""

    queryset = Customer.objects.all()
    serializer_class = serializers.CustomerSerializer
