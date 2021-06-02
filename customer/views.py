from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Invoice

from customer import serializers


class InvoiceViewSet(viewsets.ModelViewSet):
    """Manage invoice in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Invoice.objects.all()
    serializer_class = serializers.InvoiceSerializer
