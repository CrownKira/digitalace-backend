from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from core.models import (
    Invoice,
    Customer,
    SalesOrder,
    User,
    InvoiceItem,
    SalesOrderItem,
)


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer objects"""

    class Meta:
        model = Customer
        fields = (
            "id",
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
            "image",
        )
        read_only_fields = ("id", "image")
        extra_kwargs = {"image": {"allow_null": True}}

    def get_fields(self):
        fields = super().get_fields()

        try:
            if self.context["request"].method in ["GET"]:
                fields["image"] = serializers.SerializerMethodField()
            fields["agents"] = serializers.PrimaryKeyRelatedField(
                many=True,
                queryset=User.objects.filter(
                    company=self.context["request"].user.company
                ).distinct(),
            )
        except KeyError:
            pass

        return fields

    def get_image(self, obj):
        return {
            "src": obj.image.url if obj.image else "",
            "title": obj.image.name if obj.image else "",
        }


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for invoice item objects"""

    class Meta:
        model = InvoiceItem
        fields = (
            "id",
            "product",
            "invoice",
            "unit",
            "unit_price",
            "quantity",
            "amount",
        )
        read_only_fields = (
            "id",
            "invoice",
        )


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice objects"""

    class Meta:
        model = Invoice
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
            "customer",
            "salesperson",
            "sales_order",
            "status",
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

        fields["invoiceitem_set"] = InvoiceItemSerializer(
            many=True,
        )
        fields["company_name"] = serializers.SerializerMethodField()

        return fields

    def get_company_name(self, obj):
        return obj.company.name if obj.company else ""

    def validate_reference(self, reference):
        company = self.context["request"].user.company

        if self.context["request"].method in ["POST"]:
            if Invoice.objects.filter(
                company=company, reference=reference
            ).exists():
                msg = _("An invoice with this reference already exists")
                raise serializers.ValidationError(msg)
        elif (
            Invoice.objects.exclude(pk=self.instance.pk)
            .filter(company=company, reference=reference)
            .exists()
        ):
            msg = _("An invoice with this reference already exists")
            raise serializers.ValidationError(msg)

        return reference

    def _update_delete_or_create(self, instance, invoiceitems_data):
        invoiceitem_instances = instance.invoiceitem_set.all()
        invoiceitem_set_count = invoiceitem_instances.count()
        bulk_updates = []
        bulk_creates = []

        for i, invoiceitem_data in enumerate(invoiceitems_data):
            invoiceitem_data.pop("id", None)
            invoiceitem_data.pop("pk", None)
            if i < invoiceitem_set_count:
                # update
                invoiceitem_instance = invoiceitem_instances[i]
                for attr, value in invoiceitem_data.items():
                    setattr(invoiceitem_instance, attr, value)
                bulk_updates.append(invoiceitem_instance)
            else:
                # create
                bulk_creates.append(
                    # unpack first to prevent overriding
                    InvoiceItem(
                        **invoiceitem_data,
                        invoice=instance,
                    )
                )

        InvoiceItem.objects.bulk_update(
            bulk_updates,
            [
                "product",
                "invoice",
                "unit",
                "unit_price",
                "quantity",
                "amount",
            ],
        )
        # delete
        InvoiceItem.objects.filter(invoice=instance).exclude(
            pk__in=[obj.pk for obj in bulk_updates]
        ).delete()
        InvoiceItem.objects.bulk_create(bulk_creates)

    def create(self, validated_data):
        invoiceitems_data = validated_data.pop("invoiceitem_set", [])
        invoice = Invoice.objects.create(**validated_data)
        for invoiceitem_data in invoiceitems_data:
            InvoiceItem.objects.create(**invoiceitem_data, invoice=invoice)
        return invoice

    def update(self, instance, validated_data):
        invoiceitems_data = validated_data.pop("invoiceitem_set", [])
        self._update_delete_or_create(instance, invoiceitems_data)
        return super().update(instance, validated_data)


class SalesOrderItemSerializer(serializers.ModelSerializer):
    """Serializer for sales order item objects"""

    class Meta:
        model = SalesOrderItem
        fields = (
            "id",
            "product",
            "sales_order",
            "unit",
            "unit_price",
            "quantity",
            "amount",
        )
        read_only_fields = (
            "id",
            "sales_order",
        )


class SalesOrderSerializer(serializers.ModelSerializer):
    """Serializer for salesorder objects"""

    class Meta:
        model = SalesOrder
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
            "customer",
            "salesperson",
            "invoice",
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
            "invoice": {"allow_null": True},
        }

    def get_fields(self):
        fields = super().get_fields()

        fields["salesorderitem_set"] = SalesOrderItemSerializer(
            many=True,
        )
        fields["company_name"] = serializers.SerializerMethodField()

        return fields

    def get_company_name(self, obj):
        return obj.company.name if obj.company else ""

    def validate_reference(self, reference):
        company = self.context["request"].user.company

        if self.context["request"].method in ["POST"]:
            if SalesOrder.objects.filter(
                company=company, reference=reference
            ).exists():
                msg = _("A sales order with this reference already exists")
                raise serializers.ValidationError(msg)
        elif (
            SalesOrder.objects.exclude(pk=self.instance.pk)
            .filter(company=company, reference=reference)
            .exists()
        ):
            msg = _("A sales order with this reference already exists")
            raise serializers.ValidationError(msg)

        return reference

    def _update_delete_or_create(self, instance, salesorderitems_data):
        salesorderitem_instances = instance.salesorderitem_set.all()
        salesorderitem_set_count = salesorderitem_instances.count()
        bulk_updates = []
        bulk_creates = []

        for i, salesorderitem_data in enumerate(salesorderitems_data):
            salesorderitem_data.pop("id", None)
            salesorderitem_data.pop("pk", None)
            if i < salesorderitem_set_count:
                # update
                salesorderitem_instance = salesorderitem_instances[i]
                for attr, value in salesorderitem_data.items():
                    setattr(salesorderitem_instance, attr, value)
                bulk_updates.append(salesorderitem_instance)
            else:
                # create
                bulk_creates.append(
                    # unpack first to prevent overriding
                    SalesOrderItem(
                        **salesorderitem_data,
                        sales_order=instance,
                    )
                )

        SalesOrderItem.objects.bulk_update(
            bulk_updates,
            [
                "product",
                "sales_order",
                "unit",
                "unit_price",
                "quantity",
                "amount",
            ],
        )
        # delete
        SalesOrderItem.objects.filter(sales_order=instance).exclude(
            pk__in=[obj.pk for obj in bulk_updates]
        ).delete()
        SalesOrderItem.objects.bulk_create(bulk_creates)

    def create(self, validated_data):
        salesorderitems_data = validated_data.pop("salesorderitem_set", [])
        invoice = validated_data.get("invoice")
        sales_order = SalesOrder.objects.create(**validated_data)
        for salesorderitem_data in salesorderitems_data:
            SalesOrderItem.objects.create(
                **salesorderitem_data, sales_order=sales_order
            )
        # https://code.djangoproject.com/ticket/18638
        # assignment for one-to-one doesn't work as expected
        if invoice:
            invoice.sales_order = sales_order
            invoice.save()

        return sales_order

    def update(self, instance, validated_data):
        salesorderitems_data = validated_data.pop("salesorderitem_set", [])

        invoice = validated_data.get("invoice")
        if invoice:
            try:
                # try to remove reference from previous invoice
                instance_invoice = instance.invoice
                instance_invoice.sales_order = None
                instance_invoice.save()
            except SalesOrder.invoice.RelatedObjectDoesNotExist:
                pass

            # assign sales order to new invoice
            invoice.sales_order = instance
            invoice.save()

        elif "invoice" in validated_data:
            try:
                invoice = Invoice.objects.get(sales_order=instance)
                invoice.sales_order = None
                invoice.save()
            except Invoice.DoesNotExist:
                pass

        self._update_delete_or_create(instance, salesorderitems_data)
        return super().update(instance, validated_data)
