from core.views import BaseAttrViewSet, BaseAssetAttrViewSet
from core.models import (
    Product,
    ProductCategory,
    Payslip,
    Role,
    Department,
    User,
    Company,
)

from django_filters import rest_framework as filters

from company import serializers


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


class EmployeeViewSet(BaseAssetAttrViewSet):
    """Manage employee in the database"""

    queryset = User.objects.all()
    serializer_class = serializers.EmployeeSerializer
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
        "department",
        "role",
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

    def perform_create(self, serializer):
        company = Company.objects.create(
            name=serializer.validated_data.get("company", "")
        )
        serializer.save(company=company)
