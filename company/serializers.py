from rest_framework import serializers

from core.models import Product, ProductCategory


class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for product objects"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            if self.context["request"].method in ["GET"]:
                self.fields["image"] = serializers.SerializerMethodField()
        except KeyError:
            pass

    class Meta:
        model = ProductCategory
        fields = ("id", "company", "name", "image")
        read_only_fields = ("id", "company")

    def get_image(self, obj):
        # TODO: use this syntax: return "default" if x is None else x
        return obj.image.url if obj.image else ""


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product objects"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            if self.context["request"].method in ["GET"]:
                self.fields["image"] = serializers.SerializerMethodField()
                self.fields["thumbnail"] = serializers.SerializerMethodField()
        except KeyError:
            pass

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
