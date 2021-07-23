from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters

from rest_framework import viewsets, mixins

from core.views import (
    BaseAttrViewSet,
    BaseAssetAttrViewSet,
    BaseDocumentViewSet,
)
from core.models import (
    Product,
    ProductCategory,
    Payslip,
    Role,
    Department,
    Designation,
    User,
    PaymentMethod,
    Adjustment,
)
from core.utils import validate_bulk_reference_uniqueness
from company import serializers
from user.serializers import OwnerProfileSerializer


# for debug
# def create(self, request, *args, **kwargs):
#     serializer = self.get_serializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     self.perform_create(serializer)
#     headers = self.get_success_headers(serializer.data)
#     return Response(
#         serializer.data, status=status.HTTP_201_CREATED, headers=headers
#     )


class AdjustmentFilter(filters.FilterSet):
    class Meta:
        model = Adjustment
        fields = {
            "reference": ["icontains", "exact"],
            "date": ["gte", "lte"],
        }


class AdjustmentViewSet(BaseDocumentViewSet):
    """Manage customer in the database"""

    queryset = Adjustment.objects.all()
    serializer_class = serializers.AdjustmentSerializer
    filterset_class = AdjustmentFilter
    search_fields = [
        "reference",
        "date",
        "status",
        "mode",
        "reason",
    ]


class UserFilter(filters.FilterSet):
    class Meta:
        model = get_user_model()
        fields = {
            "email": ["exact"],
        }


class ListUserViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Base viewset for listing users"""

    ordering_fields = "__all__"
    ordering = ["-id"]
    filterset_class = UserFilter
    queryset = get_user_model().objects.all()

    def get_serializer_class(self):

        # TODO: make a PublicProfileSerializer
        return OwnerProfileSerializer


class ProductCategoryViewSet(BaseAssetAttrViewSet):
    """Manage product category in the database"""

    queryset = ProductCategory.objects.all()
    serializer_class = serializers.ProductCategorySerializer
    search_fields = [
        "name",
    ]


class ProductFilter(filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            "reference": ["exact"],
            "name": ["icontains"],
            "stock": ["lt", "gt", "lte", "gte", "exact"],
            "sales": ["lt", "gt", "lte", "gte", "exact"],
            "category": ["exact"],
        }


class ProductViewSet(BaseAttrViewSet):
    """Manage product in the database"""

    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer
    filterset_class = ProductFilter
    search_fields = [
        "name",
        "reference",
        "unit_price",
        "category__name",
    ]

    def get_queryset(self):
        user = self.request.user
        company = user.company
        product_qs = self.queryset if user.is_staff else user.product_set
        return product_qs.filter(category__company=company).distinct()

    # def get_queryset(self):
    #     company = self.request.user.company
    #     return Product.objects.filter(category__company=company)

    def perform_bulk_create(self, serializer):
        validate_bulk_reference_uniqueness(serializer.validated_data)
        return self.perform_create(serializer)

    def perform_bulk_update(self, serializer):
        validate_bulk_reference_uniqueness(serializer.validated_data)
        return self.perform_update(serializer)


class PaymentMethodViewSet(BaseAssetAttrViewSet):
    """Manage payment methods in the database"""

    queryset = PaymentMethod.objects.all()
    serializer_class = serializers.PaymentMethodSerializer
    search_fields = [
        "id",
        "name",
    ]


class PayslipViewSet(BaseAssetAttrViewSet):
    """Manage payslip in the database"""

    queryset = Payslip.objects.all()
    serializer_class = serializers.PayslipSerializer
    search_fields = [
        "id",
        "user__name",
        "date",
        "year",
        "month",
        "payment_method",
        "bank",
        "status",
    ]


class RoleViewSet(BaseAssetAttrViewSet):
    """Manage roles in the database"""

    queryset = Role.objects.all()
    serializer_class = serializers.RoleSerializer
    search_fields = [
        "id",
        "name",
        "permissions",
    ]


class DepartmentViewSet(BaseAssetAttrViewSet):
    """Manage departments in the database"""

    queryset = Department.objects.all()
    serializer_class = serializers.DepartmentSerializer
    search_fields = [
        "id",
        "name",
    ]


class DesignationViewSet(BaseAttrViewSet):
    """Manage designations in the database"""

    queryset = Designation.objects.all()
    serializer_class = serializers.DesignationSerializer
    search_fields = [
        "id",
        "name",
    ]

    def get_queryset(self):
        company = self.request.user.company
        return self.queryset.filter(department__company=company).distinct()


class EmployeeFilter(filters.FilterSet):
    class Meta:
        model = User
        fields = {
            "name": ["icontains"],
            "designation__department": ["exact"],
            "designation": ["exact"],
            "roles": ["exact"],
        }


class EmployeeViewSet(BaseAttrViewSet):
    """Manage employee in the database"""

    queryset = get_user_model().objects.all()
    serializer_class = serializers.EmployeeSerializer
    filterset_class = EmployeeFilter
    # TODO: remove id from all search fields?
    # TODO: reduce possible search fields
    search_fields = [
        "name",
        "first_name",
        "last_name",
        "email",
        "designation__department__name",
        "roles__name",
    ]

    def get_queryset(self):
        company = self.request.user.company
        return self.queryset.filter(is_staff=False, company=company).distinct()

    def perform_create(self, serializer):
        company = self.request.user.company
        serializer.save(company=company)
