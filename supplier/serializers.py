from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
)

from core.models import (
    Receive,
    Supplier,
    PurchaseOrder,
    ReceiveItem,
    PurchaseOrderItem,
)
from core.utils import validate_reference_uniqueness
from customer.serializers import (
    LineItemSerializer,
    DocumentSerializer,
    _update_lineitems,
)


def _update_supplier_history(instance):
    supplier = instance.supplier
    date = instance.date
    if supplier.first_seen is None:
        supplier.first_seen = date
    supplier.last_seen = date
    supplier.save()


class SupplierSerializer(BulkSerializerMixin, serializers.ModelSerializer):
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
            "first_seen",
            "last_seen",
        )
        read_only_fields = (
            "id",
            "first_seen",
            "last_seen",
        )
        extra_kwargs = {"image": {"allow_null": True}}
        list_serializer_class = BulkListSerializer

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

    class Meta(DocumentSerializer.Meta):
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

    def _update_destroy_or_create_items(self, instance, receiveitems_data):
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

    def _get_calculated_fields(self, validated_data):
        discount_rate = validated_data.pop("discount_rate")
        gst_rate = validated_data.pop("gst_rate")
        receiveitem_set = validated_data.pop("receiveitem_set")
        # TODO: fix round down behavior
        # https://stackoverflow.com/questions/20457038/how-to-round-to-2-decimals-with-python
        # round quantity, unit_price, gst_rate and discount rate first
        # then round the rest at the end of calculation
        receiveitem_set = [
            {
                **receiveitem,
                "amount": round(
                    round(receiveitem.get("quantity"))
                    * round(receiveitem.get("unit_price"), 2),
                    2,
                ),
            }
            for receiveitem in receiveitem_set
        ]
        total_amount = sum(
            [
                # recalculate amount here since it has been rounded up
                round(receiveitem.get("quantity"))
                * round(receiveitem.get("unit_price"), 2)
                for receiveitem in receiveitem_set
            ]
        )
        discount_rate = round(discount_rate, 2)
        gst_rate = round(gst_rate, 2)
        discount_amount = total_amount * discount_rate / 100
        net = total_amount * (1 - discount_rate / 100)
        gst_amount = net * gst_rate / 100
        grand_total = net * (1 + gst_rate / 100)

        return {
            "total_amount": round(total_amount, 2),
            "discount_rate": discount_rate,
            "gst_rate": gst_rate,
            "discount_amount": round(discount_amount, 2),
            "gst_amount": round(gst_amount, 2),
            "net": round(net, 2),
            "grand_total": round(grand_total, 2),
            "receiveitem_set": receiveitem_set,
        }

    def create(self, validated_data):
        validated_data = {
            **validated_data,
            **self._get_calculated_fields(validated_data),
        }

        receiveitems_data = validated_data.pop("receiveitem_set", [])
        receive = Receive.objects.create(**validated_data)
        for receiveitem_data in receiveitems_data:
            ReceiveItem.objects.create(**receiveitem_data, receive=receive)
        _update_supplier_history(receive)
        return receive

    def update(self, instance, validated_data):
        validated_data = {
            **validated_data,
            **self._get_calculated_fields(validated_data),
        }

        receiveitems_data = validated_data.pop("receiveitem_set", [])
        _update_lineitems(
            instance,
            validated_data,
            "receive",
            receiveitems_data,
            "receiveitem_set",
            ReceiveItem,
            fields=[
                "product",
                "receive",
                "unit",
                "unit_price",
                "quantity",
                "amount",
            ],
            adjust_up=True,
            affect_sales=False,
        )
        updated_instance = super().update(instance, validated_data)
        _update_supplier_history(updated_instance)
        return updated_instance


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

    class Meta(DocumentSerializer.Meta):
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
            "receive": {"allow_null": True, "required": False},
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

    def _get_calculated_fields(self, validated_data):
        discount_rate = validated_data.pop("discount_rate")
        gst_rate = validated_data.pop("gst_rate")
        purchaseorderitem_set = validated_data.pop("purchaseorderitem_set")
        # TODO: fix round down behavior
        # https://stackoverflow.com/questions/20457038/how-to-round-to-2-decimals-with-python
        # round quantity, unit_price, gst_rate and discount rate first
        # then round the rest at the end of calculation
        purchaseorderitem_set = [
            {
                **purchaseorderitem,
                "amount": round(
                    round(purchaseorderitem.get("quantity"))
                    * round(purchaseorderitem.get("unit_price"), 2),
                    2,
                ),
            }
            for purchaseorderitem in purchaseorderitem_set
        ]
        total_amount = sum(
            [
                # recalculate amount here since it has been rounded up
                round(purchaseorderitem.get("quantity"))
                * round(purchaseorderitem.get("unit_price"), 2)
                for purchaseorderitem in purchaseorderitem_set
            ]
        )
        discount_rate = round(discount_rate, 2)
        gst_rate = round(gst_rate, 2)
        discount_amount = total_amount * discount_rate / 100
        net = total_amount * (1 - discount_rate / 100)
        gst_amount = net * gst_rate / 100
        grand_total = net * (1 + gst_rate / 100)

        return {
            "total_amount": round(total_amount, 2),
            "discount_rate": discount_rate,
            "gst_rate": gst_rate,
            "discount_amount": round(discount_amount, 2),
            "gst_amount": round(gst_amount, 2),
            "net": round(net, 2),
            "grand_total": round(grand_total, 2),
            "purchaseorderitem_set": purchaseorderitem_set,
        }

    def create(self, validated_data):
        validated_data = {
            **validated_data,
            **self._get_calculated_fields(validated_data),
        }

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

        _update_supplier_history(purchase_order)
        return purchase_order

    def update(self, instance, validated_data):
        validated_data = {
            **validated_data,
            **self._get_calculated_fields(validated_data),
        }

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

        _update_lineitems(
            instance,
            validated_data,
            "purchase_order",
            purchaseorderitems_data,
            "purchaseorderitem_set",
            PurchaseOrderItem,
            fields=[
                "product",
                "purchase_order",
                "unit",
                "unit_price",
                "quantity",
                "amount",
            ],
            affect_stock=False,
            affect_sales=False,
        )

        updated_instance = super().update(instance, validated_data)
        _update_supplier_history(updated_instance)
        return updated_instance
