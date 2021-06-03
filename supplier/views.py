from core.pagination import CustomPagination
from core.views import BaseClassAttrForViewSet

from core.models import Receive

from supplier import serializers


class ReceiveViewSet(BaseClassAttrForViewSet):
    """Manage Receive in the database"""
    queryset = Receive.objects.all()
    serializer_class = serializers.ReceiveSerializer
    pagination_class = CustomPagination
