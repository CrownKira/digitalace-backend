from rest_framework import pagination


class CustomPagination(pagination.LimitOffsetPagination):
    def _params_to_int(self, qs):
        qs = qs[1:]
        qs = qs[:-1]
        return [int(str_id) for str_id in qs.split(",")]

    def paginate_queryset(self, queryset, request, view=None):
        """Custom pagination"""
        range = self.request.query_params.get("range", None)
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None

        self.count = self.get_count(queryset)
        self.offset = self.get_offset(request)

        self.request = request
        if self.count == 0 or self.offset > self.count:
            return []
        return list(queryset[self.offset : self.offset + self.limit])
