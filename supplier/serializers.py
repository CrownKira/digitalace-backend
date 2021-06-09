from rest_framework import serializers

from core.models import Receive, Supplier, PurchaseOrder


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier objects"""

    image = serializers.SerializerMethodField()

    class Meta:
        model = Supplier
        fields = (
            "id",
            "company",
            "attention",
            "name",
            "address",
            "city",
            "state",
            "zipcode",
            "contact",
            "term",
            "phone_no",
            "email",
            "payables",
            "image"
            # "first_seen",
            # "last_seen",
        )
        read_only_fields = ("id", "company")

    def get_image(self, obj):
        return obj.image.url if obj.image else ""

    def validate(self, attrs):
        """Validate image and add it to validated_data"""
        image = self.initial_data.get("image", None)
        # TODO: validate if it is a valid image
        if image:
            attrs["image"] = image
        return attrs


class ReceiveSerializer(serializers.ModelSerializer):
    """Serializer for Receive objects"""

    class Meta:
        model = Receive
        fields = (
            "id",
            "company",
            "date",
            "description",
            "payment_date",
            "payment_method",
            "payment_note",
            "gst_rate",
            "discount_rate",
            "gst_amount",
            "discount_amount",
            "net",
            "total_amount",
            "grand_total",
            "status",
            "supplier",
            "purchase_order",
        )
        read_only_fields = ("id", "company")


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for Receive objects"""

    class Meta:
        model = PurchaseOrder
        fields = (
            "id",
            "company",
            "date",
            "description",
            "payment_date",
            "payment_method",
            "payment_note",
            "gst_rate",
            "discount_rate",
            "gst_amount",
            "discount_amount",
            "net",
            "total_amount",
            "grand_total",
            "status",
            "supplier",
        )
        read_only_fields = ("id", "company")
