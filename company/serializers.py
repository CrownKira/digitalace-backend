from rest_framework import serializers

from core.models import Product, ProductCategory


class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for product objects"""

    class Meta:
        model = ProductCategory
        fields = ("id", "company", "name")
        read_only_fields = ("id", "company")


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product objects"""

    image = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()

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

    def get_image(self, obj):
        return obj.image.url if obj.image else ""

    def get_thumbnail(self, obj):
        return obj.thumbnail.url if obj.thumbnail else ""

    def validate(self, attrs):
        """Validate image and thumbnail and add it to validated_data"""
        image = self.initial_data.get("image", None)
        thumbnail = self.initial_data.get("thumbnail", None)
        # TODO: validate if it is a valid image
        if image:
            attrs["image"] = image
        if thumbnail:
            attrs["thumbnail"] = thumbnail
        return attrs
