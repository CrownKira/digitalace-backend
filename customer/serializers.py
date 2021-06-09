from rest_framework import serializers

from core.models import Invoice, Customer, SalesOrder


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer objects"""

    image = serializers.SerializerMethodField()

    class Meta:
        model = Customer
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
            "receivables",
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


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice objects"""

    class Meta:
        model = Invoice
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
            "customer",
            "salesperson",
            "sales_order",
        )
        read_only_fields = ("id", "company")


class SalesOrderSerializer(serializers.ModelSerializer):
    """Serializer for salesorder objects"""

    class Meta:
        model = SalesOrder
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
            "customer",
            "salesperson",
        )
        read_only_fields = ("id", "company")
