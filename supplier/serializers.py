from rest_framework import serializers

from core.models import Receive


class ReceiveSerializer(serializers.ModelSerializer):
    """Serializer for Receive objects"""

    class Meta:
        model = Receive
        fields = (
            'id', 'supplier', 'purchase_order',
            'company',
            'date', 'payment_date',
            'gst_rate', 'discount_rate',
            'gst_amount', 'discount_amount',
            'net', 'total_amount', 'grand_total',
        )
        read_only_fields = ('id',)
