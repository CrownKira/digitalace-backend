from django_filters import rest_framework as filters

from core.views import BaseAssetAttrViewSet
from core.models import Receive, Supplier, PurchaseOrder
from supplier import serializers


class SupplierFilter(filters.FilterSet):
    class Meta:
        model = Supplier
        fields = {
            "reference": ["exact"],
            "name": ["icontains"],
            "last_seen": ["lt", "gt", "lte", "gte", "exact"],
        }


class SupplierViewSet(BaseAssetAttrViewSet):
    """Manage Supplier in the database"""

    queryset = Supplier.objects.all()
    serializer_class = serializers.SupplierSerializer
    filterset_class = SupplierFilter
    search_fields = [
        "name",
        "attention",
        "email",
        "phone_no",
        "payables",
    ]


class ReceiveFilter(filters.FilterSet):
    class Meta:
        model = Receive
        fields = {
            "reference": ["icontains"],
        }


class ReceiveViewSet(BaseAssetAttrViewSet):
    """Manage Receive in the database"""

    queryset = Receive.objects.all()
    serializer_class = serializers.ReceiveSerializer
    filterset_class = ReceiveFilter
    search_fields = [
        "reference",
        "date",
        "supplier__name",
        "supplier__address",
        "purchase_order__reference",
        "status",
        "grand_total",
    ]

    def _get_calculated_fields(self, serializer):
        discount_rate = serializer.validated_data.pop("discount_rate")
        gst_rate = serializer.validated_data.pop("gst_rate")
        receiveitem_set = serializer.validated_data.pop("receiveitem_set")
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
        grand_total = net * (1 - gst_rate / 100)

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


class PurchaseOrderFilter(filters.FilterSet):
    class Meta:
        model = PurchaseOrder
        fields = {
            "reference": ["icontains"],
        }


class PurchaseOrderViewSet(BaseAssetAttrViewSet):
    """Manage Supplier in the database"""

    queryset = PurchaseOrder.objects.all()
    serializer_class = serializers.PurchaseOrderSerializer

    filterset_class = PurchaseOrderFilter
    search_fields = [
        "reference",
        "date",
        "supplier__name",
        "supplier__address",
        "receive__reference",
        "status",
        "grand_total",
    ]

    def _get_calculated_fields(self, serializer):
        discount_rate = serializer.validated_data.pop("discount_rate")
        gst_rate = serializer.validated_data.pop("gst_rate")
        purchaseorderitem_set = serializer.validated_data.pop(
            "purchaseorderitem_set"
        )
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
        grand_total = net * (1 - gst_rate / 100)

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
