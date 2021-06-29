from django_filters import rest_framework as filters

from core.views import BaseAssetAttrViewSet
from core.models import Invoice, Customer, SalesOrder
from customer import serializers


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
        # TODO: fix round down behavior
        # https://stackoverflow.com/questions/20457038/how-to-round-to-2-decimals-with-python
        # round quantity, unit_price, gst_rate and discount rate first
        # then round the rest at the end of calculation
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

        return {
            "total_amount": round(total_amount, 2),
            "discount_rate": discount_rate,
            "gst_rate": gst_rate,
            "discount_amount": round(discount_amount, 2),
            "gst_amount": round(gst_amount, 2),
            "net": round(net, 2),
            "grand_total": round(grand_total, 2),
            "invoiceitem_set": invoiceitem_set,
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
        "invoice__reference",
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
