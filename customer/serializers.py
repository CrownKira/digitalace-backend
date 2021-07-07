from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model


from rest_framework import serializers

from core.models import (
    Invoice,
    Customer,
    SalesOrder,
    InvoiceItem,
    SalesOrderItem,
    CreditNote,
    CreditNoteItem,
    CreditsApplication,
)


class LineItemSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True

    def validate_amount(self, amount):
        if amount < 0:
            msg = _("Amount cannot be negative")
            raise serializers.ValidationError(msg)
        return amount

    def validate_quantity(self, quantity):
        if quantity < 0:
            msg = _("Quantity cannot be negative")
            raise serializers.ValidationError(msg)
        return quantity

    def validate_unit_price(self, unit_price):
        if unit_price < 0:
            msg = _("Unit price cannot be negative")
            raise serializers.ValidationError(msg)
        return unit_price


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True

    def validate_gst_rate(self, gst_rate):
        if gst_rate < 0:
            msg = _("GST Rate cannot be negative")
            raise serializers.ValidationError(msg)
        return gst_rate

    def validate_discount_rate(self, discount_rate):
        if discount_rate < 0:
            msg = _("Discount Rate cannot be negative")
            raise serializers.ValidationError(msg)
        return discount_rate


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer objects"""

    class Meta:
        model = Customer
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
            "receivables",
            "image",
            "unused_credits",
        )
        read_only_fields = (
            "id",
            "image",
            "unused_credits",
        )
        extra_kwargs = {"image": {"allow_null": True}}

    def get_fields(self):
        fields = super().get_fields()

        try:
            if self.context["request"].method in ["GET"]:
                fields["image"] = serializers.SerializerMethodField()
            fields["agents"] = serializers.PrimaryKeyRelatedField(
                many=True,
                queryset=get_user_model()
                .objects.filter(company=self.context["request"].user.company)
                .distinct(),
            )
        except KeyError:
            pass

        return fields

    def get_image(self, obj):
        return {
            "src": obj.image.url if obj.image else "",
            "title": obj.image.name if obj.image else "",
        }

    # TODO: create a validate_reference global function
    def validate_reference(self, reference):
        company = self.context["request"].user.company

        if self.context["request"].method in ["POST"]:
            if Customer.objects.filter(
                company=company, reference=reference
            ).exists():
                msg = _("A customer with this reference already exists")
                raise serializers.ValidationError(msg)
        elif (
            Customer.objects.exclude(pk=self.instance.pk)
            .filter(company=company, reference=reference)
            .exists()
        ):
            msg = _("A customer with this reference already exists")
            raise serializers.ValidationError(msg)

        return reference


class CreditNoteItemSerializer(LineItemSerializer):
    """Serializer for credit_note item objects"""

    class Meta:
        model = CreditNoteItem
        fields = (
            "id",
            "product",
            "credit_note",
            "unit",
            "unit_price",
            "quantity",
            "amount",
        )
        read_only_fields = (
            "id",
            "credit_note",
        )


class CreditNoteSerializer(DocumentSerializer):
    """Serializer for Credit Note objects"""

    class Meta:
        model = CreditNote
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
            "customer",
            "salesperson",
            # "sales_order",
            "status",
            "refund",
            "credits_used",
            "credits_remaining",
            "created_from",
        )
        read_only_fields = (
            "id",
            "company",
            "gst_amount",
            "discount_amount",
            "net",
            "total_amount",
            "grand_total",
            "credits_used",
            "credits_remaining",
        )

    def get_fields(self):
        fields = super().get_fields()

        fields["creditnoteitem_set"] = CreditNoteItemSerializer(
            many=True,
        )
        fields["company_name"] = serializers.SerializerMethodField()

        return fields

    def get_company_name(self, obj):
        return obj.company.name if obj.company else ""

    def validate_refund(self, refund):
        if refund < 0:
            msg = _("Refund cannot be negative")
            raise serializers.ValidationError(msg)
        return refund

    def validate_reference(self, reference):
        company = self.context["request"].user.company

        if self.context["request"].method in ["POST"]:
            if CreditNote.objects.filter(
                company=company, reference=reference
            ).exists():
                msg = _("A credit note with this reference already exists")
                raise serializers.ValidationError(msg)
        elif (
            CreditNote.objects.exclude(pk=self.instance.pk)
            .filter(company=company, reference=reference)
            .exists()
        ):
            msg = _("A credit note with this reference already exists")
            raise serializers.ValidationError(msg)

        return reference

    def _update_delete_or_create(self, instance, creditnoteitems_data):
        creditnoteitem_instances = instance.creditnoteitem_set.all()
        creditnoteitem_set_count = creditnoteitem_instances.count()
        bulk_updates = []
        bulk_creates = []

        for i, creditnoteitem_data in enumerate(creditnoteitems_data):
            creditnoteitem_data.pop("id", None)
            creditnoteitem_data.pop("pk", None)
            if i < creditnoteitem_set_count:
                # update
                creditnoteitem_instance = creditnoteitem_instances[i]
                for attr, value in creditnoteitem_data.items():
                    setattr(creditnoteitem_instance, attr, value)
                bulk_updates.append(creditnoteitem_instance)
            else:
                # create
                bulk_creates.append(
                    # unpack first to prevent overriding
                    CreditNoteItem(
                        **creditnoteitem_data,
                        credit_note=instance,
                    )
                )

        CreditNoteItem.objects.bulk_update(
            bulk_updates,
            [
                "product",
                "credit_note",
                "unit",
                "unit_price",
                "quantity",
                "amount",
            ],
        )
        # delete
        CreditNoteItem.objects.filter(credit_note=instance).exclude(
            pk__in=[obj.pk for obj in bulk_updates]
        ).delete()
        CreditNoteItem.objects.bulk_create(bulk_creates)

    def create(self, validated_data):
        creditnoteitems_data = validated_data.pop("creditnoteitem_set", [])
        credit_note = CreditNote.objects.create(**validated_data)
        for creditnoteitem_data in creditnoteitems_data:
            CreditNoteItem.objects.create(
                **creditnoteitem_data, credit_note=credit_note
            )

        # calculate unused credits and store in db instead of calculate
        # on every request for customer api since this will slow down api response
        customer = credit_note.customer
        customer.unused_credits += credit_note.credits_remaining
        customer.save()

        return credit_note

    def update(self, instance, validated_data):
        creditnoteitems_data = validated_data.pop("creditnoteitem_set", [])
        customer = validated_data.get("customer")
        self._update_delete_or_create(instance, creditnoteitems_data)
        credit_note = super().update(instance, validated_data)

        customer.unused_credits += (
            credit_note.credits_remaining - instance.credits_remaining
        )
        customer.save()

        return credit_note


class CreditsApplicationSerializer(serializers.ModelSerializer):
    """Serializer for credits application"""

    # TODO: when delete, add back to credits remaining
    class Meta:
        model = CreditsApplication
        fields = (
            "id",
            "invoice",
            "credit_note",
            "date",
            "amount_to_credit",
        )
        read_only_fields = (
            "id",
            "date",
        )


class InvoiceItemSerializer(LineItemSerializer):
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


class InvoiceSerializer(DocumentSerializer):
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
            "balance_due",
            "credits_applied",
        )
        read_only_fields = (
            "id",
            "company",
            "gst_amount",
            "discount_amount",
            "net",
            "total_amount",
            "grand_total",
            "balance_due",
            "credits_applied",
        )

    def get_fields(self):
        fields = super().get_fields()

        if self.context["request"].method in ["GET"]:
            fields[
                "creditsapplication_set"
            ] = serializers.SerializerMethodField()
        else:
            fields["creditsapplication_set"] = CreditsApplicationSerializer(
                many=True,
            )
        fields["invoiceitem_set"] = InvoiceItemSerializer(
            many=True,
        )
        fields["company_name"] = serializers.SerializerMethodField()

        return fields

    def get_creditsapplication_set(self, obj):
        # return obj.company.name if obj.company else ""

        credit_notes = CreditNote.objects.filter(
            customer=obj.customer
        ).distinct()

        return CreditNoteSerializer(credit_notes, many=True).data

    def get_company_name(self, obj):
        return obj.company.name if obj.company else ""

    def validate(self, attrs):
        ## customer is required?
        ## split post and patch vs get from validated data?
        customer = attrs.get("customer")
        creditsapplication_set = attrs.get("creditsapplication_set")

        if any(
            [
                creditsapplication.get("credit_note").customer.id
                != customer.id
                for creditsapplication in creditsapplication_set
            ]
        ):
            msg = _(
                "Credits from other customers cannot be applied to this invoice"
            )
            raise serializers.ValidationError(msg)

        if self.context["request"].method in ["PUT", "PATCH"]:
            if (
                self.instance.customer.id != customer.id
                and self.instance.credits_applied > 0
            ):
                msg = _(
                    "The customer for this invoice cannot be changed. This customer's credits have been applied to this invoice"
                )
                raise serializers.ValidationError(msg)

        return attrs

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

    # def validate_customer(self, customer):

    #     if not all_unique(
    #         [
    #             creditsapplication.get("credit_note")
    #             for creditsapplication in creditsapplication_set
    #         ]
    #     ):
    #         msg = _('The customer for this invoice cannot be changed. This customer\'s credits have been applied to this invoice')
    #         raise serializers.ValidationError(msg)

    #     return customer

    def validate_creditsapplication_set(self, creditsapplication_set):
        def all_unique(x):
            seen = set()
            return not any(i in seen or seen.add(i) for i in x)

        if not all_unique(
            [
                creditsapplication.get("credit_note")
                for creditsapplication in creditsapplication_set
            ]
        ):
            msg = _("Duplicate credit notes not allowed")
            raise serializers.ValidationError(msg)

        return creditsapplication_set

    def _update_delete_or_create_items(self, instance, invoiceitems_data):
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

    def _update_delete_or_create_credit_applications(
        self, instance, creditapplications_data
    ):
        creditapplication_instances = instance.creditapplication_set.all()
        creditapplication_set_count = creditapplication_instances.count()
        bulk_updates = []
        bulk_creates = []

        for i, creditapplication_data in enumerate(creditapplications_data):
            creditapplication_data.pop("id", None)
            creditapplication_data.pop("pk", None)
            if i < creditapplication_set_count:
                # update
                creditapplication_instance = creditapplication_instances[i]
                for attr, value in creditapplication_data.items():
                    setattr(creditapplication_instance, attr, value)
                bulk_updates.append(creditapplication_instance)
            else:
                # create
                bulk_creates.append(
                    # unpack first to prevent overriding
                    CreditsApplication(
                        **creditapplication_data,
                        invoice=instance,
                    )
                )

        CreditsApplication.objects.bulk_update(
            bulk_updates,
            [
                "invoice",
                "credit_note",
                "date",
                "amount_to_credit",
            ],
        )
        # delete
        CreditsApplication.objects.filter(invoice=instance).exclude(
            pk__in=[obj.pk for obj in bulk_updates]
        ).delete()
        CreditsApplication.objects.bulk_create(bulk_creates)

    def create(self, validated_data):
        invoiceitems_data = validated_data.pop("invoiceitem_set", [])
        creditsapplications_data = validated_data.pop(
            "creditsapplication_set", []
        )
        invoice = Invoice.objects.create(**validated_data)
        for invoiceitem_data in invoiceitems_data:
            InvoiceItem.objects.create(**invoiceitem_data, invoice=invoice)
        for creditsapplication_data in creditsapplications_data:
            CreditsApplication.objects.create(
                **creditsapplication_data, invoice=invoice
            )
        return invoice

    def update(self, instance, validated_data):
        invoiceitems_data = validated_data.pop("invoiceitem_set", [])
        creditsapplications_data = validated_data.pop(
            "creditsapplication_set", []
        )
        self._update_delete_or_create_items(instance, invoiceitems_data)
        self._update_delete_or_create_credits_applications(
            instance, creditsapplications_data
        )
        return super().update(instance, validated_data)


class SalesOrderItemSerializer(LineItemSerializer):
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


class SalesOrderSerializer(DocumentSerializer):
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
            "invoice_set",
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
        # invoice = validated_data.get("invoice")
        sales_order = SalesOrder.objects.create(**validated_data)
        for salesorderitem_data in salesorderitems_data:
            SalesOrderItem.objects.create(
                **salesorderitem_data, sales_order=sales_order
            )

        # TODO: create invoice from sales order, can't assign
        # https://code.djangoproject.com/ticket/18638
        # assignment for one-to-one doesn't work as expected
        # if invoice:
        #     invoice.sales_order = sales_order
        #     invoice.save()

        return sales_order

    def update(self, instance, validated_data):
        salesorderitems_data = validated_data.pop("salesorderitem_set", [])

        # invoice = validated_data.get("invoice")
        # if invoice:
        #     try:
        #         # try to remove reference from previous invoice
        #         instance_invoice = instance.invoice
        #         instance_invoice.sales_order = None
        #         instance_invoice.save()
        #     except SalesOrder.invoice.RelatedObjectDoesNotExist:
        #         pass

        #     # assign sales order to new invoice
        #     invoice.sales_order = instance
        #     invoice.save()

        # elif "invoice" in validated_data:
        #     try:
        #         invoice = Invoice.objects.get(sales_order=instance)
        #         invoice.sales_order = None
        #         invoice.save()
        #     except Invoice.DoesNotExist:
        #         pass

        self._update_delete_or_create(instance, salesorderitems_data)
        return super().update(instance, validated_data)
