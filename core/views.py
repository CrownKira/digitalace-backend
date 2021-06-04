from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
import re


class BaseClassAttrForViewSet(viewsets.ModelViewSet):
    """Base attr for viewsets"""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_int(self, qs):
        """Convert string to list of integer"""
        qs = qs[1:]
        qs = qs[:-1]
        qs = qs.split(":")
        qsid = qs[0].strip('"')
        splited = qs[1]
        if "[" and "]" in splited:
            splited = re.sub(r"[\[\]]", "", splited)
            intsplit = [int(str_id) for str_id in splited.split(",")]
            return {qsid + "__in": intsplit}
        return {qsid: splited}

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
        if filter is not None:
            filtered = self._params_to_int(filter)
            queryset = queryset.filter(**filtered)
        if sort is not None:
            sorted = self._param_to_str(sort)
            if sorted[1] == "DESC":
                queryset = queryset.order_by("-" + sorted[0])
            else:
                queryset = queryset.order_by(sorted[0])
        return queryset
