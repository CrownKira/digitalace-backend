from django_filters import rest_framework as filters

from core.views import BaseAttrViewSet, BaseAssetAttrViewSet
from core.models import (
    Product,
    ProductCategory,
    Payslip,
    Role,
    Department,
    Designation,
    User,
)
from company import serializers


# for debug
# def create(self, request, *args, **kwargs):
#     serializer = self.get_serializer(data=request.data)
#     serializer.is_valid(raise_exception=True)
#     self.perform_create(serializer)
#     headers = self.get_success_headers(serializer.data)
#     return Response(
#         serializer.data, status=status.HTTP_201_CREATED, headers=headers
#     )


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
        "category__name",
        "supplier__name",
        "name",
        "unit",
        "cost",
        "unit_price",
        "stock",
        "sales",
    ]

    def get_queryset(self):
        company = self.request.user.company
        return Product.objects.filter(category__company=company)

    def perform_update(self, serializer):
        serializer.save()


class PayslipViewset(BaseAssetAttrViewSet):
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
            "designation__department": ["exact"],
            "designation": ["exact"],
            "roles": ["exact"],
        }


class EmployeeViewSet(BaseAttrViewSet):
    """Manage employee in the database"""

    queryset = User.objects.all()
    serializer_class = serializers.EmployeeSerializer
    filterset_class = EmployeeFilter
    # TODO: remove id from all search fields?
    # TODO: reduce possible search fields
    search_fields = [
        "id",
        # "password",
        # "last_login",
        # "is_superuser",
        # "company",
        # "is_active",
        # "is_staff",
        "email",
        "name",
        # "department__name",
        "roles__name",
        # "image",
        # "resume",
        "first_name",
        "last_name",
        "residential_address",
        "postal_code",
        "ic_no",
        "nationality",
        "gender",
        "date_of_birth",
        "date_of_commencement",
        "date_of_cessation",
        "phone_no",
    ]

    def get_queryset(self):
        company = self.request.user.company
        return self.queryset.filter(is_staff=False, company=company).distinct()

    def perform_create(self, serializer):
        company = self.request.user.company
        serializer.save(company=company)
