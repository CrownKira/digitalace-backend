from rest_framework.pagination import PageNumberPagination
from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 1000
