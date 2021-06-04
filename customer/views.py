from core.pagination import CustomPagination
from core.views import BaseClassAttrForViewSet

from core.models import Invoice, Customer

from customer import serializers


class InvoiceViewSet(BaseClassAttrForViewSet):
    """Manage invoice in the database"""
    queryset = Invoice.objects.all()
    serializer_class = serializers.InvoiceSerializer
    pagination_class = CustomPagination


class CustomerViewSet(BaseClassAttrForViewSet):
    """Manage customer in the database"""
    queryset = Customer.objects.all()
    serializer_class = serializers.CustomerSerializer
    pagination_class = CustomPagination
