from core.views import BaseAssetAttrViewSet
from core.models import Product, ProductCategory

from company import serializers


class ProductCategoryViewSet(BaseAssetAttrViewSet):
    """Manage product category in the database"""

    queryset = ProductCategory.objects.all()
    serializer_class = serializers.ProductSerializer


class ProductViewSet(BaseAssetAttrViewSet):
    """Manage product in the database"""

    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer

    def get_queryset(self):
        company = self.request.user.company
        return Product.objects.filter(category__company=company)
