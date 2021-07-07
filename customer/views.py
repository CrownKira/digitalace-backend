from decimal import Decimal

from django.utils.timezone import now

from django_filters import rest_framework as filters
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models.transaction import CreditNoteItem
from core.views import BaseAssetAttrViewSet, BaseAttrViewSet
from core.models import (
    Invoice,
    Customer,
    SalesOrder,
    CreditNote,
    CreditsApplication,
)
from customer import serializers
from core.pagination import StandardResultsSetPagination


class CustomerFilter(filters.FilterSet):
    class Meta:
        model = Customer
        fields = {
            "reference": ["exact"],
            "name": ["icontains"],
            "last_seen": ["lt", "gt", "lte", "gte", "exact"],
            "agents": ["exact"],
        }


class CustomerViewSet(BaseAssetAttrViewSet):
    """Manage customer in the database"""

    queryset = Customer.objects.all()
    serializer_class = serializers.CustomerSerializer
    filterset_class = CustomerFilter
    search_fields = [
        "name",
        "attention",
        "email",
        "phone_no",
        "receivables",
    ]


class CreditsApplicationFilter(filters.FilterSet):
    class Meta:
        model = CreditsApplication
        fields = {"invoice": ["exact"], "credit_note__customer": ["exact"]}


class CreditsApplicationViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.DestroyModelMixin
):
    """Manage designations in the database"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination
    ordering_fields = "__all__"
    ordering = ["-id"]
    queryset = CreditsApplication.objects.all()
    serializer_class = serializers.CreditsApplicationSerializer
    search_fields = [
        "id",
        "date",
        "credit_note__reference",
        "amount_to_credit",
    ]

    # TODO: perform_create()
    def get_queryset(self):
        company = self.request.user.company
        return self.queryset.filter(invoice__company=company).distinct()

    def perform_destroy(self, instance):
        amount_to_credit = instance.amount_to_credit
        invoice = instance.invoice
        customer = invoice.customer
        credit_note = instance.credit_note

        invoice.credits_applied -= amount_to_credit
        invoice.balance_due += amount_to_credit
        invoice.save()

        customer.unused_credits += amount_to_credit
        customer.save()

        credit_note.credits_used -= amount_to_credit
        credit_note.credits_remaining += amount_to_credit
        credit_note.save()

        instance.delete()


class CreditNoteFilter(filters.FilterSet):
    class Meta:
        model = CreditNote
        fields = {
            "reference": ["icontains", "exact"],
        }


class CreditNoteViewSet(BaseAssetAttrViewSet):
    """Manage credit note in the database"""

    queryset = CreditNote.objects.all()
    serializer_class = serializers.CreditNoteSerializer
    filterset_class = CreditNoteFilter
    search_fields = [
        "reference",
        "date",
        "customer__name",
        "customer__address",
        "sales_order__reference",
        "status",
        "grand_total",
    ]

    def _get_calculated_fields(self, serializer):
        # assume all positive
        discount_rate = serializer.validated_data.pop("discount_rate")
        gst_rate = serializer.validated_data.pop("gst_rate")
        creditnoteitem_set = serializer.validated_data.pop(
            "creditnoteitem_set"
        )
        credits_used = Decimal("0.00")
        # TODO: remove this later after implement apply credits to invoice from credit note
        if self.request.method in ["PUT", "PATCH"]:
            credits_used = serializer.instance.credits_used

        refund = serializer.validated_data.pop("refund")

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
        grand_total = net * (1 - gst_rate / 100)
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





    def perform_create(self, serializer):
        company = self.request.user.company
        serializer.save(
            company=company, **self._get_calculated_fields(serializer)
        )

    def perform_update(self, serializer):
        company = self.request.user.company
        serializer.save(
            company=company, **self._get_calculated_fields(serializer)
        )


class InvoiceFilter(filters.FilterSet):
    class Meta:
        model = Invoice
        fields = {
            # https://docs.djangoproject.com/en/3.2/ref/models/lookups/#module-django.db.models.lookups
            # https://django-filter.readthedocs.io/en/stable/ref/filterset.html#declaring-filterable-fields
            # reference__icontains=
            # there is no reference__exact=, just reference= will do
            "reference": ["icontains", "exact"],
        }


class InvoiceViewSet(BaseAssetAttrViewSet):
    """Manage invoice in the database"""

    queryset = Invoice.objects.all()
    serializer_class = serializers.InvoiceSerializer
    filterset_class = InvoiceFilter
    search_fields = [
        "reference",
        "date",
        "customer__name",
        "customer__address",
        "sales_order__reference",
        "status",
        "grand_total",
    ]

    def _get_calculated_fields(self, serializer):
        discount_rate = serializer.validated_data.pop("discount_rate")
        gst_rate = serializer.validated_data.pop("gst_rate")
        invoiceitem_set = serializer.validated_data.pop("invoiceitem_set")
        customer = serializer.validated_data.pop("customer")
        creditsapplication_set = serializer.validated_data.pop(
            "creditsapplication_set"
        )
        # TODO: fix round down behavior
        # https://stackoverflow.com/questions/20457038/how-to-round-to-2-decimals-with-python
        # round quantity, unit_price, gst_rate and discount rate first
        # then round the rest at the end of calculation
        # TODO: assign invoice later after create or update
        ## only for creation
        credits_applied = 0
        new_creditsapplication_set = []
        for credits_application in creditsapplication_set:
            # update customer unused credits
            amount_to_credit = round(
                credits_application.get("amount_to_credit"), 2
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

            customer.unused_credits -= new_amount_to_credit
            customer.save()

            new_creditsapplication_set.append(
                {
                    **credits_application,
                    "date": now,
                    "amount_to_credit": new_amount_to_credit,
                }
            )

        # creditsapplication_set = [
        #     {
        #         **credits_application,
        #         "date": now,
        #         "amount_to_credit": round(
        #             credits_application.get("amount_to_credit"), 2
        #         ),
        #     }
        #     for credits_application in creditsapplication_set
        # ]
        # credits_applied = sum(
        #     [
        #         max(
        #             credits_application.get("amount_to_credit"),
        #             CreditNote.objects.get(
        #                 reference=credits_application.get(
        #                     "reference"
        #                 ).credits_remaining
        #             ),
        #         )
        #         for credits_application in creditsapplication_set
        #     ]
        # )
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
        grand_total = net * (1 - gst_rate / 100)
        balance_due = grand_total - credits_applied

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

    def perform_create(self, serializer):
        company = self.request.user.company
        serializer.save(
            company=company, **self._get_calculated_fields(serializer)
        )

    def perform_update(self, serializer):
        company = self.request.user.company
        serializer.save(
            company=company, **self._get_calculated_fields(serializer)
        )


class SalesOrderFilter(filters.FilterSet):
    class Meta:
        model = SalesOrder
        fields = {
            "reference": ["icontains", "exact"],
        }


class SalesOrderViewSet(BaseAssetAttrViewSet):
    """Manage customer in the database"""

    queryset = SalesOrder.objects.all()
    serializer_class = serializers.SalesOrderSerializer
    filterset_class = SalesOrderFilter
    search_fields = [
        "reference",
        "date",
        "customer__name",
        "customer__address",
        # "invoice__reference",
        "status",
        "grand_total",
    ]

    def _get_calculated_fields(self, serializer):
        discount_rate = serializer.validated_data.pop("discount_rate")
        gst_rate = serializer.validated_data.pop("gst_rate")
        salesorderitem_set = serializer.validated_data.pop(
            "salesorderitem_set"
        )
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
        grand_total = net * (1 - gst_rate / 100)

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

    def perform_create(self, serializer):
        company = self.request.user.company
        serializer.save(
            company=company, **self._get_calculated_fields(serializer)
        )

    def perform_update(self, serializer):
        company = self.request.user.company
        serializer.save(
            company=company, **self._get_calculated_fields(serializer)
        )
