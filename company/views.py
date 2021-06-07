from core.pagination import CustomPagination
from core.views import BaseClassAttrForViewSet

from core.models import Product

from company import serializers


class ProductViewSet(BaseClassAttrForViewSet):
    """Manage product in the database"""
    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer
    pagination_class = CustomPagination
