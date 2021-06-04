from rest_framework import serializers

from core.models import Receive, Supplier


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


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier objects"""

    class Meta:
        model = Supplier
        fields = (
            'id', 'company', 'attention',
            'name', 'address', 'area',
            'contact', 'term', 'phone_no'
        )
        read_only_fields = ('id',)
