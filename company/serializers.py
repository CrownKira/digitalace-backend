from rest_framework import serializers

from core.models import Product, ProductCategory


class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for product objects"""

    class Meta:
        model = ProductCategory
        fields = ("id", "company", "name")
        read_only_fields = ("id",)


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product objects"""

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "supplier",
            "name",
            "unit",
            "cost",
            "unit_price",
            "image",
            "thumbnail",
            "stock",
            "sales",
        )
        read_only_fields = ("id",)
