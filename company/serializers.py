from rest_framework import serializers

from core.models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product objects"""

    class Meta:
        model = Product
        fields = (
            'id', 'category', 'supplier', 'name',
            'unit', 'cost', 'unit_price'
        )
        read_only_fields = ('id',)
