from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from core.models import Invoice, Customer, SalesOrder, User, InvoiceItem


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

        return fields

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
        InvoiceItem.objects.exclude(
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
