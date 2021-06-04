from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


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
            self.offset = range[0] - 1
            self.limit = range[1] + 1
        if self.limit is None:
            return None
        self.count = self.get_count(queryset)
        self.request = request
        if self.count == 0 or self.offset > self.count:
            return []
        return list(queryset[self.offset: self.limit])

    def get_paginated_response(self, data):
        total_items = self.count
        item_starting_index = self.offset + 1
        item_ending_index = self.limit - 1

        content_range = 'items {0}-{1}/{2}'.format(
            item_starting_index,
            item_ending_index,
            total_items
        )

        headers = {'Content-Range': content_range}

        return Response(data, headers=headers)
