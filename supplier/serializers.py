from rest_framework import serializers

from core.models import Receive, Supplier, PurchaseOrder


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier objects"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            if self.context["request"].method in ["GET"]:
                self.fields["image"] = serializers.SerializerMethodField()
            else:
                self.fields["image"] = serializers.ImageField(
                    allow_empty_file=True, allow_null=True
                )
        except KeyError:
            pass

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
        return {
            "src": obj.image.url if obj.image else "",
            "title": obj.image.name if obj.image else "",
        }


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
