from rest_framework import serializers

from core.models import Invoice


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
        )
        read_only_fields = ('id',)