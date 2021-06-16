from django.contrib.auth import get_user_model

from rest_framework import serializers

from core.models import (
    Product,
    ProductCategory,
    Payslip,
    Role,
    Department,
    Designation,
    Customer,
)
from user.serializers import UserSerializer


class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for product objects"""

    class Meta:
        model = ProductCategory
        fields = ("id", "company", "name", "image")
        read_only_fields = ("id", "company")

    def get_fields(self):
        fields = super().get_fields()
        if self.context["request"].method in ["GET"]:
            fields["image"] = serializers.SerializerMethodField()
        return fields

    def get_image(self, obj):
        return {
            "src": obj.image.url if obj.image else "",
            "title": obj.image.name if obj.image else "",
        }


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product objects"""

    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "supplier",
            "name",
            "unit",
            "cost",
            "unit_price",
            "image",
            "thumbnail",
            "stock",
            "sales",
        )
        read_only_fields = ("id",)

    def get_fields(self):
        fields = super().get_fields()
        if self.context["request"].method in ["GET"]:
            fields["image"] = serializers.SerializerMethodField()
            fields["thumbnail"] = serializers.SerializerMethodField()
        else:
            fields["image"] = serializers.ImageField(
                allow_empty_file=True, allow_null=True
            )
            fields["thumbnail"] = serializers.ImageField(
                allow_empty_file=True, allow_null=True
            )
        return fields

    def get_image(self, obj):
        return {
            "src": obj.image.url if obj.image else "",
            "title": obj.image.name if obj.image else "",
        }

    def get_thumbnail(self, obj):
        return {
            "src": obj.thumbnail.url if obj.thumbnail else "",
            "title": obj.thumbnail.name if obj.thumbnail else "",
        }


class PayslipSerializer(serializers.ModelSerializer):
    """Serializer for payslip objects"""

    class Meta:
        model = Payslip
        fields = (
            "id",
            "user",
            "company",
            "date",
            "year",
            "month",
            "basic_salary",
            "total_allowances",
            "total_deductions",
            "sale_price",
            "commission",
            "commission_amt",
            "net_pay",
            "payment_method",
            "bank",
            "status",
            "comment",
        )
        read_only_fields = ("id", "company")


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for role objects"""

    class Meta:
        model = Role
        fields = ("id", "name", "permissions")
        read_only_fields = ("id",)


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for department objects"""

    class Meta:
        model = Department
        fields = (
            "id",
            "name",
        )
        read_only_fields = ("id",)


class DesignationSerializer(serializers.ModelSerializer):
    """Serializer for designation objects"""

    class Meta:
        model = Designation
        fields = (
            "id",
            "name",
        )
        read_only_fields = ("id",)


class EmployeeSerializer(UserSerializer):
    """Serializer for employee objects"""

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "password",
            # "last_login",
            # "is_superuser",
            # "company_name",
            # "is_active",
            # "is_staff",
            "email",
            "name",
            "department",
            "roles",
            "image",
            "resume",
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
            "permissions",
        )

        read_only_fields = ("id",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def get_fields(self):
        fields = super().get_fields()
        if self.context["request"].method in ["GET"]:
            fields["resume"] = serializers.SerializerMethodField()
        else:
            fields["resume"] = serializers.ImageField(
                allow_empty_file=True, allow_null=True
            )
        fields["roles"] = serializers.PrimaryKeyRelatedField(
            many=True,
            queryset=Role.objects.filter(
                company=self.context["request"].user.company
            ).distinct(),
        )
        fields["customer_set"] = serializers.PrimaryKeyRelatedField(
            many=True,
            queryset=Customer.objects.filter(
                company=self.context["request"].user.company
            ).distinct(),
        )
        fields["product_set"] = serializers.PrimaryKeyRelatedField(
            many=True,
            queryset=Product.objects.filter(
                category__company=self.context["request"].user.company
            ).distinct(),
        )
        return fields
