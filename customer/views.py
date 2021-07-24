from django.utils.translation import ugettext_lazy as _

from django_filters import rest_framework as filters
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.permissions import RolePermission
from core.utils import validate_bulk_reference_uniqueness
from core.views import BaseAssetAttrViewSet, BaseDocumentViewSet
from core.models import (
    Invoice,
    Customer,
    SalesOrder,
    CreditNote,
    CreditsApplication,
)
from core.pagination import StandardResultsSetPagination
from customer.serializers import (
    CustomerSerializer,
    CreditsApplicationSerializer,
    InvoiceSerializer,
    SalesOrderSerializer,
    CreditNoteSerializer,
    _update_inventory,
)


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
    serializer_class = CustomerSerializer
    filterset_class = CustomerFilter
    search_fields = [
        "name",
        "attention",
        "email",
        "phone_no",
        "receivables",
    ]

    def get_queryset(self):
        user = self.request.user
        company = user.company
        customer_qs = self.queryset if user.is_staff else user.customer_set
        return customer_qs.filter(company=company).distinct()

    def perform_bulk_create(self, serializer):
        validate_bulk_reference_uniqueness(serializer.validated_data)
        return self.perform_create(serializer)

    def perform_bulk_update(self, serializer):
        validate_bulk_reference_uniqueness(serializer.validated_data)
        return self.perform_update(serializer)


class CreditsApplicationFilter(filters.FilterSet):
    class Meta:
        model = CreditsApplication
        fields = {
            "invoice": ["exact"],
            "credit_note": ["exact"],
            "credit_note__customer": ["exact"],
        }


class CreditsApplicationViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.DestroyModelMixin
):
    """Manage designations in the database"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, RolePermission)
    pagination_class = StandardResultsSetPagination
    ordering_fields = "__all__"
    ordering = ["-id"]
    queryset = CreditsApplication.objects.all()
    serializer_class = CreditsApplicationSerializer
    filterset_class = CreditsApplicationFilter
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
            "customer": ["exact"],
            "created_from": ["exact"],
            "date": ["gte", "lte"],
        }


class CreditNoteViewSet(BaseDocumentViewSet):
    """Manage credit note in the database"""

    queryset = CreditNote.objects.all()
    serializer_class = CreditNoteSerializer
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

    def perform_destroy(self, instance):
        for item in instance.creditnoteitem_set:
            _update_inventory(
                item.status,
                item.product,
                item.quantity,
                adjust_up=False,
                affect_sales=True,
            )
        instance.delete()


class InvoiceFilter(filters.FilterSet):
    class Meta:
        model = Invoice
        fields = {
            # https://docs.djangoproject.com/en/3.2/ref/models/lookups/#module-django.db.models.lookups
            # https://django-filter.readthedocs.io/en/stable/ref/filterset.html#declaring-filterable-fields
            # reference__icontains=
            # there is no reference__exact=, just reference= will do
            "reference": ["icontains", "exact"],
            "sales_order": ["exact"],
            "date": ["gte", "lte"],
        }


class InvoiceViewSet(BaseDocumentViewSet):
    """Manage invoice in the database"""

    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
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

    def perform_destroy(self, instance):
        for item in instance.invoiceitem_set:
            _update_inventory(
                item.status,
                item.product,
                item.quantity,
                adjust_up=True,
                affect_sales=True,
            )
        instance.delete()


class SalesOrderFilter(filters.FilterSet):
    class Meta:
        model = SalesOrder
        fields = {
            "reference": ["icontains", "exact"],
            "date": ["gte", "lte"],
        }


class SalesOrderViewSet(BaseDocumentViewSet):
    """Manage customer in the database"""

    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    filterset_class = SalesOrderFilter
    search_fields = [
        "reference",
        "date",
        "customer__name",
        "customer__address",
        "status",
        "grand_total",
    ]
