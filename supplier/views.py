from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Receive

from supplier import serializers


class ReceiveViewSet(viewsets.ModelViewSet):
    """Manage Receive in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Receive.objects.all()
    serializer_class = serializers.ReceiveSerializer
