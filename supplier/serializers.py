from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from core.models import (
    Receive,
    Supplier,
    PurchaseOrder,
    ReceiveItem,
    PurchaseOrderItem,
)
from core.utils import validate_reference_uniqueness
from customer.serializers import LineItemSerializer, DocumentSerializer


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier objects"""

    class Meta:
        model = Supplier
        fields = (
            "id",
            "reference",
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
            "image",
        )
        read_only_fields = ("id",)
        extra_kwargs = {"image": {"allow_null": True}}

    def get_fields(self):
        fields = super().get_fields()

        try:
            if self.context["request"].method in ["GET"]:
                fields["image"] = serializers.SerializerMethodField()
        except KeyError:
            pass

        return fields

    def get_image(self, obj):
        return {
            "src": obj.image.url if obj.image else "",
            "title": obj.image.name if obj.image else "",
        }

    def validate(self, attrs):
        validate_reference_uniqueness(
            self, Supplier, attrs.get("reference"), attrs.get("id")
        )
        return attrs


class ReceiveItemSerializer(LineItemSerializer):
    """Serializer for receive item objects"""

    class Meta:
        model = ReceiveItem
        fields = (
            "id",
            "product",
            "receive",
            "unit",
            "unit_price",
            "quantity",
            "amount",
        )
        read_only_fields = (
            "id",
            "receive",
        )


class ReceiveSerializer(DocumentSerializer):
    """Serializer for Receive objects"""

    class Meta:
        model = Receive
        fields = (
            "id",
            "company",
            "reference",
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
        read_only_fields = (
            "id",
            "company",
            "gst_amount",
            "discount_amount",
            "net",
            "total_amount",
            "grand_total",
        )

    def get_fields(self):
        fields = super().get_fields()

        fields["receiveitem_set"] = ReceiveItemSerializer(
            many=True,
        )
        fields["company_name"] = serializers.SerializerMethodField()

        return fields

    def get_company_name(self, obj):
        return obj.company.name if obj.company else ""

    def validate(self, attrs):
        validate_reference_uniqueness(
            self, Receive, attrs.get("reference"), attrs.get("id")
        )
        return attrs

    def _update_destroy_or_create(self, instance, receiveitems_data):
        receiveitem_instances = instance.receiveitem_set.all()
        receiveitem_set_count = receiveitem_instances.count()
        bulk_updates = []
        bulk_creates = []

        for i, receiveitem_data in enumerate(receiveitems_data):
            receiveitem_data.pop("id", None)
            receiveitem_data.pop("pk", None)
            if i < receiveitem_set_count:
                # update
                receiveitem_instance = receiveitem_instances[i]
                for attr, value in receiveitem_data.items():
                    setattr(receiveitem_instance, attr, value)
                bulk_updates.append(receiveitem_instance)
            else:
                # create
                bulk_creates.append(
                    # unpack first to prevent overriding
                    ReceiveItem(
                        **receiveitem_data,
                        receive=instance,
                    )
                )

        ReceiveItem.objects.bulk_update(
            bulk_updates,
            [
                "product",
                "receive",
                "unit",
                "unit_price",
                "quantity",
                "amount",
            ],
        )
        # delete
        ReceiveItem.objects.filter(receive=instance).exclude(
            pk__in=[obj.pk for obj in bulk_updates]
        ).delete()
        ReceiveItem.objects.bulk_create(bulk_creates)

    def create(self, validated_data):
        receiveitems_data = validated_data.pop("receiveitem_set", [])
        receive = Receive.objects.create(**validated_data)
        for receiveitem_data in receiveitems_data:
            ReceiveItem.objects.create(**receiveitem_data, receive=receive)
        return receive

    def update(self, instance, validated_data):
        receiveitems_data = validated_data.pop("receiveitem_set", [])
        self._update_destroy_or_create(instance, receiveitems_data)
        return super().update(instance, validated_data)


class PurchaseOrderItemSerializer(LineItemSerializer):
    """Serializer for purchase order item objects"""

    class Meta:
        model = PurchaseOrderItem
        fields = (
            "id",
            "product",
            "purchase_order",
            "unit",
            "unit_price",
            "quantity",
            "amount",
        )
        read_only_fields = (
            "id",
            "purchase_order",
        )


class PurchaseOrderSerializer(DocumentSerializer):
    """Serializer for Receive objects"""

    class Meta:
        model = PurchaseOrder
        fields = (
            "id",
            "company",
            "reference",
            "date",
            "description",
            # "payment_date",
            # "payment_method",
            # "payment_note",
            "gst_rate",
            "discount_rate",
            "gst_amount",
            "discount_amount",
            "net",
            "total_amount",
            "grand_total",
            "status",
            "supplier",
            "receive",
        )
        read_only_fields = (
            "id",
            "company",
            "gst_amount",
            "discount_amount",
            "net",
            "total_amount",
            "grand_total",
        )

        extra_kwargs = {
            "receive": {"allow_null": True},
        }

    def get_fields(self):
        fields = super().get_fields()

        fields["purchaseorderitem_set"] = PurchaseOrderItemSerializer(
            many=True,
        )
        fields["company_name"] = serializers.SerializerMethodField()

        return fields

    def get_company_name(self, obj):
        return obj.company.name if obj.company else ""

    def validate(self, attrs):
        validate_reference_uniqueness(
            self, PurchaseOrder, attrs.get("reference"), attrs.get("id")
        )
        return attrs

    def _update_destroy_or_create(self, instance, purchaseorderitems_data):
        purchaseorderitem_instances = instance.purchaseorderitem_set.all()
        purchaseorderitem_set_count = purchaseorderitem_instances.count()
        bulk_updates = []
        bulk_creates = []

        for i, purchaseorderitem_data in enumerate(purchaseorderitems_data):
            purchaseorderitem_data.pop("id", None)
            purchaseorderitem_data.pop("pk", None)
            if i < purchaseorderitem_set_count:
                # update
                purchaseorderitem_instance = purchaseorderitem_instances[i]
                for attr, value in purchaseorderitem_data.items():
                    setattr(purchaseorderitem_instance, attr, value)
                bulk_updates.append(purchaseorderitem_instance)
            else:
                # create
                bulk_creates.append(
                    # unpack first to prevent overriding
                    PurchaseOrderItem(
                        **purchaseorderitem_data,
                        purchase_order=instance,
                    )
                )

        PurchaseOrderItem.objects.bulk_update(
            bulk_updates,
            [
                "product",
                "purchase_order",
                "unit",
                "unit_price",
                "quantity",
                "amount",
            ],
        )
        # delete
        PurchaseOrderItem.objects.filter(purchase_order=instance).exclude(
            pk__in=[obj.pk for obj in bulk_updates]
        ).delete()
        PurchaseOrderItem.objects.bulk_create(bulk_creates)

    def create(self, validated_data):
        purchaseorderitems_data = validated_data.pop(
            "purchaseorderitem_set", []
        )
        receive = validated_data.get("receive")
        purchase_order = PurchaseOrder.objects.create(**validated_data)
        for purchaseorderitem_data in purchaseorderitems_data:
            PurchaseOrderItem.objects.create(
                **purchaseorderitem_data, purchase_order=purchase_order
            )

        if receive:
            receive.purchase_order = purchase_order
            receive.save()

        return purchase_order

    def update(self, instance, validated_data):
        purchaseorderitems_data = validated_data.pop(
            "purchaseorderitem_set", []
        )

        receive = validated_data.get("receive")
        if receive:
            try:
                instance_receive = instance.receive
                instance_receive.purchase_order = None
                instance_receive.save()
            except PurchaseOrder.receive.RelatedObjectDoesNotExist:
                pass

            receive.purchase_order = instance
            receive.save()

        elif "receive" in validated_data:
            try:
                receive = Receive.objects.get(purchase_order=instance)
                receive.purchase_order = None
                receive.save()
            except Receive.DoesNotExist:
                pass

        self._update_destroy_or_create(instance, purchaseorderitems_data)
        return super().update(instance, validated_data)
