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
        qs = qs.split(":")
        qsid = qs[0].strip('"')
        splited = qs[1]
        if "[" and "]" in splited:
            splited = splited.split('],')[0]
            splited = re.sub(r"[\[\]]", "", splited)
            intsplit = [int(str_id) for str_id in splited.split(",")]
            return {qsid + "__in": intsplit}
        splited = splited.strip(',')
        return {qsid: splited}

    def _param_to_str(self, qs):
        """Convert string to list of string"""
        qs = qs[1:]
        qs = qs[:-1]
        qs = qs.split(",")
        qs = [i.strip('"') for i in qs]
        return qs

    def _new_params_to_int(self, qs, queryset):
        """Convert string to list of integer with respecive reference"""
        qs = qs[1:]
        qs = qs[:-1]
        while qs.count('"') > 1:
            splt_char = '"'
            K = 3
            temp = qs.split(splt_char)
            res = splt_char.join(temp[:K]), splt_char.join(temp[K:])
            qs = '"' + res[1]
            fltr = res[0]
            filtered = self._params_to_int(fltr)
            queryset = queryset.filter(**filtered)
        return queryset

    def get_queryset(self):
        """Custom queryset to support filtering sorting and listing"""
        queryset = self.queryset.order_by("id")
        filter = self.request.query_params.get("filter", None)
        sort = self.request.query_params.get("sort", None)
        if filter is not None:
            queryset = self._new_params_to_int(filter, queryset)
        if sort is not None:
            sorted = self._param_to_str(sort)
            if sorted[1] == "DESC":
                queryset = queryset.order_by("-" + sorted[0])
            else:
                queryset = queryset.order_by(sorted[0])
        return queryset
