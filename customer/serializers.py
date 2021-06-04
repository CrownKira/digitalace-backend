from rest_framework import serializers

from core.models import Invoice, Customer, SalesOrder


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice objects"""

    class Meta:
        model = Invoice
        fields = (
            'id', 'date', 'payment_date',
            'gst_rate', 'discount_rate',
            'gst_amount', 'discount_amount',
            'net', 'total_amount', 'grand_total',
            'customer', 'sales_order', 'salesperson',
            'company'
        )
        read_only_fields = ('id',)


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer objects"""

    class Meta:
        model = Customer
        fields = (
            'id', 'company', 'attention', 'name', 'address',
            'area', 'contact', 'term', 'phone_no'
        )
        read_only_fields = ('id',)


class SalesOrderSerializer(serializers.ModelSerializer):
    """Serializer for salesorder objects"""

    class Meta:
        model = SalesOrder
        fields = (
            'id', 'date', 'payment_date',
            'gst_rate', 'discount_rate',
            'gst_amount', 'discount_amount',
            'net', 'total_amount', 'grand_total',
            'customer', 'salesperson', 'company'
        )
        read_only_fields = ('id',)
