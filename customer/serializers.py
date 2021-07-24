from decimal import Decimal
from datetime import datetime

from django.utils import formats
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
)

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
from core.utils import validate_reference_uniqueness, all_unique


# TODO: refactor
class LineItemSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    class Meta:
        list_serializer_class = BulkListSerializer
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


class DocumentSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    class Meta:
        list_serializer_class = BulkListSerializer
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


class CustomerSerializer(BulkSerializerMixin, serializers.ModelSerializer):
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
            "first_seen",
            "last_seen",
        )
        read_only_fields = (
            "id",
            "unused_credits",
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

    def validate(self, attrs):
        validate_reference_uniqueness(
            self, Customer, attrs.get("reference"), attrs.get("id")
        )
        return attrs


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

    class Meta(DocumentSerializer.Meta):
        model = CreditNote
        fields = (
            "id",
            "company",
            "reference",
            "date",
            "description",
            "gst_rate",
            "discount_rate",
            "gst_amount",
            "discount_amount",
            "net",
            "total_amount",
            "grand_total",
            "customer",
            "salesperson",
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

    def validate(self, attrs):
        validate_reference_uniqueness(
            self, CreditNote, attrs.get("reference"), attrs.get("id")
        )
        return attrs

    def _get_calculated_fields(self, validated_data):
        # assume all positive
        discount_rate = validated_data.pop("discount_rate")
        gst_rate = validated_data.pop("gst_rate")
        creditnoteitem_set = validated_data.pop("creditnoteitem_set")
        credits_used = Decimal("0.00")
        # TODO: remove this later after implement apply credits to invoice from credit note
        if self.context["request"].method in ["PUT", "PATCH"]:
            credits_used = self.instance.credits_used

        refund = validated_data.pop("refund")

        creditnoteitem_set = [
            {
                **creditnoteitem,
                "amount": round(
                    round(creditnoteitem.get("quantity"))
                    * round(creditnoteitem.get("unit_price"), 2),
                    2,
                ),
            }
            for creditnoteitem in creditnoteitem_set
        ]
        total_amount = sum(
            [
                # recalculate amount here since it has been rounded up
                round(creditnoteitem.get("quantity"))
                * round(creditnoteitem.get("unit_price"), 2)
                for creditnoteitem in creditnoteitem_set
            ]
        )
        discount_rate = round(discount_rate, 2)
        gst_rate = round(gst_rate, 2)
        discount_amount = total_amount * discount_rate / 100
        net = total_amount * (1 - discount_rate / 100)
        gst_amount = net * gst_rate / 100
        grand_total = net * (1 + gst_rate / 100)
        credits_remaining = grand_total - credits_used
        refund = min(credits_remaining, round(refund, 2))
        credits_remaining -= refund

        return {
            "total_amount": round(total_amount, 2),
            "discount_rate": discount_rate,
            "gst_rate": gst_rate,
            "discount_amount": round(discount_amount, 2),
            "gst_amount": round(gst_amount, 2),
            "net": round(net, 2),
            "grand_total": round(grand_total, 2),
            "creditnoteitem_set": creditnoteitem_set,
            "credits_used": credits_used,
            "credits_remaining": credits_remaining,
            "refund": refund,
        }

    def create(self, validated_data):
        validated_data = {
            **validated_data,
            **self._get_calculated_fields(validated_data),
        }

        creditnoteitems_data = validated_data.pop("creditnoteitem_set", [])
        credit_note = CreditNote.objects.create(**validated_data)
        for creditnoteitem_data in creditnoteitems_data:
            CreditNoteItem.objects.create(
                **creditnoteitem_data, credit_note=credit_note
            )

        # calculate unused credits and store in db instead of calculate
        # on every request for customer api since this will slow down api response
        customer = credit_note.customer
        _update_customer_credits(customer, credit_note.credits_remaining)

        return credit_note

    def update(self, instance, validated_data):
        validated_data = {
            **validated_data,
            **self._get_calculated_fields(validated_data),
        }

        creditnoteitems_data = validated_data.pop("creditnoteitem_set", [])
        customer = validated_data.get("customer")
        _update_lineitems(
            instance,
            validated_data,
            "credit_note",
            creditnoteitems_data,
            "creditnoteitem_set",
            CreditNoteItem,
            fields=[
                "product",
                "credit_note",
                "unit",
                "unit_price",
                "quantity",
                "amount",
            ],
            adjust_up=True,
            affect_sales=True,
        )

        credit_note = super().update(instance, validated_data)

        _update_customer_credits(
            customer,
            credit_note.credits_remaining - instance.credits_remaining,
        )

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
        extra_kwargs = {"amount_to_credit": {"required": False}}


def _update_customer_credits(customer, offset):
    customer.unused_credits += offset
    customer.save()


def _update_customer_history(instance):
    customer = instance.customer
    date = instance.date
    if customer.first_seen is None:
        customer.first_seen = date
    customer.last_seen = date
    customer.save()


def _update_inventory(
    status, product, quantity, adjust_up=True, affect_sales=True
):
    # add to stock and remove from sales
    if status in ["DFT", "CC"]:
        return

    if adjust_up:
        product.stock += quantity
        if affect_sales:
            product.sales -= quantity
    else:
        product.stock -= quantity
        if affect_sales:
            product.sales += quantity
    product.save()


def _update_lineitems(
    instance,
    validated_data,
    instance_name,
    lineitems_data,
    item_set_name,
    LineItemModel,
    fields,
    affect_stock=True,
    affect_sales=True,
    adjust_up=True,
):
    lineitem_instances = getattr(instance, item_set_name).all()
    lineitem_set_count = lineitem_instances.count()
    bulk_updates = []
    bulk_creates = []

    for i, lineitem_data in enumerate(lineitems_data):
        if affect_stock:
            _update_inventory(
                validated_data.get("status"),
                lineitem_data.get("product"),
                lineitem_data.get("quantity"),
                adjust_up=adjust_up,
                affect_sales=affect_sales,
            )

        lineitem_data.pop("id", None)
        lineitem_data.pop("pk", None)
        if i < lineitem_set_count:
            # update
            lineitem_instance = lineitem_instances[i]
            if affect_stock:
                _update_inventory(
                    instance.status,
                    lineitem_instance.product,
                    lineitem_instance.quantity,
                    adjust_up=not adjust_up,
                    affect_sales=affect_sales,
                )

            for attr, value in lineitem_data.items():
                setattr(lineitem_instance, attr, value)
            bulk_updates.append(lineitem_instance)
        else:
            # create
            bulk_creates.append(
                # unpack first to prevent overriding
                LineItemModel(
                    **lineitem_data,
                    **{instance_name: instance},
                )
            )

    LineItemModel.objects.bulk_update(bulk_updates, fields)
    # delete
    LineItemModel.objects.filter(**{instance_name: instance}).exclude(
        pk__in=[obj.pk for obj in bulk_updates]
    ).delete()
    LineItemModel.objects.bulk_create(bulk_creates)


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

    class Meta(DocumentSerializer.Meta):
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

        fields["creditsapplication_set"] = CreditsApplicationSerializer(
            many=True,
        )
        fields["invoiceitem_set"] = InvoiceItemSerializer(
            many=True,
        )
        fields["company_name"] = serializers.SerializerMethodField()

        return fields

    def get_company_name(self, obj):
        return obj.company.name if obj.company else ""

    def validate(self, attrs):
        customer = attrs.get("customer")
        creditsapplication_set = attrs.get("creditsapplication_set", [])

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
                self.instance.customer
                and self.instance.customer.id != customer.id
                and self.instance.credits_applied > 0
            ):
                msg = _(
                    "The customer for this invoice cannot be changed. This customer's credits have been applied to this invoice"
                )
                raise serializers.ValidationError(msg)

        validate_reference_uniqueness(
            self, Invoice, attrs.get("reference"), attrs.get("id")
        )
        return attrs

    def validate_creditsapplication_set(self, creditsapplication_set):

        if not all_unique(
            [
                creditsapplication.get("credit_note")
                for creditsapplication in creditsapplication_set
            ]
        ):
            msg = _("Duplicate credit notes not allowed")
            raise serializers.ValidationError(msg)

        return creditsapplication_set

    def _get_calculated_fields(self, validated_data):

        discount_rate = validated_data.pop("discount_rate")
        gst_rate = validated_data.pop("gst_rate")
        invoiceitem_set = validated_data.pop("invoiceitem_set")
        customer = validated_data.get("customer")
        creditsapplication_set = validated_data.pop(
            "creditsapplication_set", []
        )
        # TODO: fix round down behavior
        # https://stackoverflow.com/questions/20457038/how-to-round-to-2-decimals-with-python
        # round quantity, unit_price, gst_rate and discount rate first
        # then round the rest at the end of calculation
        # TODO: assign invoice later after create or update

        credits_applied = Decimal("0.00")
        if self.context["request"].method in ["PUT", "PATCH"]:
            credits_applied = self.instance.credits_applied
        new_creditsapplication_set = []
        for credits_application in creditsapplication_set:
            # update customer unused credits
            amount_to_credit = round(
                credits_application.get("amount_to_credit") or Decimal("0.00"),
                2,
            )
            credit_note = credits_application.get("credit_note")

            # next time when come to this, credits remaining will reduce
            new_amount_to_credit = min(
                amount_to_credit,
                credit_note.credits_remaining,
            )

            credits_applied += new_amount_to_credit
            credit_note.credits_remaining -= new_amount_to_credit
            credit_note.credits_used += new_amount_to_credit
            credit_note.save()

            _update_customer_credits(customer, -new_amount_to_credit)

            new_creditsapplication_set.append(
                {
                    **credits_application,
                    "date": formats.date_format(datetime.now(), "Y-m-d"),
                    "amount_to_credit": new_amount_to_credit,
                }
            )

        invoiceitem_set = [
            {
                **invoiceitem,
                "amount": round(
                    round(invoiceitem.get("quantity"))
                    * round(invoiceitem.get("unit_price"), 2),
                    2,
                ),
            }
            for invoiceitem in invoiceitem_set
        ]
        total_amount = sum(
            [
                # recalculate amount here since it has been rounded up
                round(invoiceitem.get("quantity"))
                * round(invoiceitem.get("unit_price"), 2)
                for invoiceitem in invoiceitem_set
            ]
        )
        discount_rate = round(discount_rate, 2)
        gst_rate = round(gst_rate, 2)
        discount_amount = total_amount * discount_rate / 100
        net = total_amount * (1 - discount_rate / 100)
        gst_amount = net * gst_rate / 100
        grand_total = net * (1 + gst_rate / 100)
        balance_due = grand_total - credits_applied

        if balance_due < 0:
            msg = _("Credits Applied cannot be more than Grand Total")
            raise serializers.ValidationError(msg)

        return {
            "total_amount": round(total_amount, 2),
            "discount_rate": discount_rate,
            "gst_rate": gst_rate,
            "discount_amount": round(discount_amount, 2),
            "gst_amount": round(gst_amount, 2),
            "net": round(net, 2),
            "grand_total": round(grand_total, 2),
            "invoiceitem_set": invoiceitem_set,
            "creditsapplication_set": new_creditsapplication_set,
            "credits_applied": credits_applied,
            "balance_due": balance_due,
        }

    def create(self, validated_data):
        validated_data = {
            **validated_data,
            **self._get_calculated_fields(validated_data),
        }

        invoiceitems_data = validated_data.pop("invoiceitem_set", [])
        creditsapplications_data = validated_data.pop(
            "creditsapplication_set", []
        )
        invoice = Invoice.objects.create(**validated_data)
        for invoiceitem_data in invoiceitems_data:
            InvoiceItem.objects.create(**invoiceitem_data, invoice=invoice)
        # TODO: bulk create?
        for creditsapplication_data in creditsapplications_data:
            if creditsapplication_data.get("amount_to_credit") > 0:
                creditsapplication_data.pop("invoice", None)
                CreditsApplication.objects.create(
                    **creditsapplication_data, invoice=invoice
                )

        _update_customer_history(invoice)
        return invoice

    def update(self, instance, validated_data):
        validated_data = {
            **validated_data,
            **self._get_calculated_fields(validated_data),
        }

        invoiceitems_data = validated_data.pop("invoiceitem_set", [])
        creditsapplications_data = validated_data.pop(
            "creditsapplication_set", []
        )

        _update_lineitems(
            instance,
            validated_data,
            "invoice",
            invoiceitems_data,
            "invoiceitem_set",
            InvoiceItem,
            fields=[
                "product",
                "invoice",
                "unit",
                "unit_price",
                "quantity",
                "amount",
            ],
            adjust_up=False,
            affect_sales=True,
        )

        for creditsapplication_data in creditsapplications_data:
            if creditsapplication_data.get("amount_to_credit") > 0:
                creditsapplication_data.pop("invoice", None)
                CreditsApplication.objects.create(
                    **creditsapplication_data, invoice=instance
                )
        updated_instance = super().update(instance, validated_data)
        _update_customer_history(updated_instance)
        return updated_instance


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

    class Meta(DocumentSerializer.Meta):
        model = SalesOrder
        fields = (
            "id",
            "company",
            "reference",
            "date",
            "description",
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

        try:
            if self.context["request"].method in ["GET", "PUT", "PATCH"]:
                fields["invoice_set"] = serializers.PrimaryKeyRelatedField(
                    many=True,
                    queryset=Invoice.objects.filter(
                        company=self.context["request"].user.company
                    ).distinct(),
                )

        except KeyError:
            pass

        return fields

    def get_company_name(self, obj):
        return obj.company.name if obj.company else ""

    def validate(self, attrs):
        validate_reference_uniqueness(
            self, SalesOrder, attrs.get("reference"), attrs.get("id")
        )
        return attrs

    def _get_calculated_fields(self, validated_data):
        discount_rate = validated_data.pop("discount_rate")
        gst_rate = validated_data.pop("gst_rate")
        salesorderitem_set = validated_data.pop("salesorderitem_set")
        # TODO: fix round down behavior
        # https://stackoverflow.com/questions/20457038/how-to-round-to-2-decimals-with-python
        # round quantity, unit_price, gst_rate and discount rate first
        # then round the rest at the end of calculation
        salesorderitem_set = [
            {
                **salesorderitem,
                "amount": round(
                    round(salesorderitem.get("quantity"))
                    * round(salesorderitem.get("unit_price"), 2),
                    2,
                ),
            }
            for salesorderitem in salesorderitem_set
        ]
        total_amount = sum(
            [
                # recalculate amount here since it has been rounded up
                round(salesorderitem.get("quantity"))
                * round(salesorderitem.get("unit_price"), 2)
                for salesorderitem in salesorderitem_set
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
            "salesorderitem_set": salesorderitem_set,
        }

    def create(self, validated_data):
        validated_data = {
            **validated_data,
            **self._get_calculated_fields(validated_data),
        }

        salesorderitems_data = validated_data.pop("salesorderitem_set", [])
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

        _update_customer_history(sales_order)
        return sales_order

    def update(self, instance, validated_data):
        validated_data = {
            **validated_data,
            **self._get_calculated_fields(validated_data),
        }

        salesorderitems_data = validated_data.pop("salesorderitem_set", [])

        _update_lineitems(
            instance,
            validated_data,
            "sales_order",
            salesorderitems_data,
            "salesorderitem_set",
            SalesOrderItem,
            fields=[
                "product",
                "sales_order",
                "unit",
                "unit_price",
                "quantity",
                "amount",
            ],
            affect_stock=False,
            affect_sales=False,
        )

        updated_instance = super().update(instance, validated_data)
        _update_customer_history(updated_instance)
        return updated_instance
