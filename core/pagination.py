from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from collections import OrderedDict


class CustomPagination(LimitOffsetPagination):
    def _params_to_int(self, qs):
        qs = qs[1:]
        qs = qs[:-1]
        return [int(str_id) for str_id in qs.split(",")]

    def paginate_queryset(self, queryset, request, view=None):
        """Custom pagination"""
        range = request.query_params.get("range", None)
        self.offset = 0
        self.limit = None
        if range is not None:
            range = self._params_to_int(range)
            self.offset = range[0]
            self.limit = range[1] + 1
        if self.limit is None:
            return None
        self.count = self.get_count(queryset)
        self.request = request
        if self.count == 0 or self.offset > self.count:
            return []
        return list(queryset[self.offset: self.limit])

    def get_paginated_response(self, data):
        # self.next_link = self.request.build_absolute_uri().rsplit('/', 1)[0]
        # self.next_link = self.next_link + '/?'
        # filter = self.request.query_params.get("filter", None)
        # if filter is not None:
        #    self.next_link = self.next_link + 'filter=' + filter
        # self.next_link = self.next_link + '&range='
        return Response(
            OrderedDict(
                [
                    ("count", self.count),
                    # ("next", self.get_next_link()),
                    # ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )
