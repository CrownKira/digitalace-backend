from rest_framework import serializers

from core.models import Invoice, Customer, SalesOrder


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
            # "first_seen",
            # "last_seen",
        )
        read_only_fields = ("id", "company")


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
