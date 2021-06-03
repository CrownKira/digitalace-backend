from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

# from core.pagination import CustomPagination
import re

from core.models import Invoice

from customer import serializers


class InvoiceViewSet(viewsets.ModelViewSet):
    """Manage invoice in the database"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Invoice.objects.all()
    serializer_class = serializers.InvoiceSerializer
    # pagination_class = CustomPagination

    def _params_to_int(self, qs):
        """Convert string to list of integer"""
        qs = qs[1:]
        qs = qs[:-1]
        qs = re.sub(r"[\[\]]", "", qs)
        qs = qs.split(":")
        split2 = qs[1]
        intsplit = [int(str_id) for str_id in split2.split(",")]
        print("testcase")
        print(intsplit)
        print(qs[0])
        return {qs[0] + "__in": intsplit}

    def _param_to_str(self, qs):
        """Convert string to list of string"""
        qs = qs[1:]
        qs = qs[:-1]
        qs = qs.split(",")
        qs = [i.strip('"') for i in qs]
        return qs

    def get_queryset(self):
        """Custom queryset to support filtering sorting and listing"""
        queryset = self.queryset.order_by("id")
        filter = self.request.query_params.get("filter", None)
        sort = self.request.query_params.get("sort", None)
        print(filter)
        if filter is not None:
            filtered = self._params_to_int(filter)
            queryset = queryset.exclude(**filtered)
        if sort is not None:
            sorted = self._param_to_str(sort)
            if sorted[1] == "DESC":
                queryset = queryset.order_by("-" + sorted[0])
            else:
                queryset = queryset.order_by(sorted[0])
        return queryset
