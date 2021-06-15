from rest_framework import serializers

from core.models import Invoice, Customer, SalesOrder, User
from core.relations import PrimaryKeyListRelatedField


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer objects"""

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
        read_only_fields = ("id", "company", "image")

    def get_fields(self):
        fields = super().get_fields()
        if self.context["request"].method in ["GET"]:
            fields["image"] = serializers.SerializerMethodField()
        else:
            fields["image"] = serializers.ImageField(
                allow_empty_file=True, allow_null=True
            )
        fields["agents"] = PrimaryKeyListRelatedField(
            many=True,
            queryset=User.objects.filter(
                company=self.context["request"].user.company
            ).distinct(),
        )
        return fields

    def get_image(self, obj):
        return {
            "src": obj.image.url if obj.image else "",
            "title": obj.image.name if obj.image else "",
        }

    def create(self, validated_data):
        agents = validated_data.pop("agents", None)
        customer = super().create(self, validated_data)
        if agents:
            customer.agents.set(agents[0])

        return customer

    def update(self, instance, validated_data):
        agents = validated_data.pop("agents", None)
        customer = super().update(instance, validated_data)
        if agents:
            customer.agents.set(agents[0])

        return customer


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
