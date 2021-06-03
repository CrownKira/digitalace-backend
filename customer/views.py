from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.pagination import CustomPagination
from core.views import BaseClassAttrForViewSet
import re

from core.models import Invoice

from customer import serializers


class InvoiceViewSet(BaseClassAttrForViewSet):
    """Manage invoice in the database"""

    queryset = Invoice.objects.all()
    serializer_class = serializers.InvoiceSerializer
    pagination_class = CustomPagination
