from rest_framework import serializers

from core.models import Product, ProductCategory, Payslip, Role, Department


class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for product objects"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            if self.context["request"].method in ["GET"]:
                self.fields["image"] = serializers.SerializerMethodField()
        except KeyError:
            pass

    class Meta:
        model = ProductCategory
        fields = ("id", "company", "name", "image")
        read_only_fields = ("id", "company")

    def get_image(self, obj):
        # TODO: use this syntax: return "default" if x is None else x
        return obj.image.url if obj.image else ""


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product objects"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            if self.context["request"].method in ["GET"]:
                self.fields["image"] = serializers.SerializerMethodField()
                self.fields["thumbnail"] = serializers.SerializerMethodField()
        except KeyError:
            pass

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

    def get_image(self, obj):
        return obj.image.url if obj.image else ""

    def get_thumbnail(self, obj):
        return obj.thumbnail.url if obj.thumbnail else ""


class PayslipSerializer(serializers.ModelSerializer):
    """Serializer for Payslip objects"""

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
    """Serializer for Role objects"""

    class Meta:
        model = Role
        fields = ("id", "name", "permissions")
        read_only_fields = ("id",)


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department objects"""

    class Meta:
        model = Department
        fields = (
            "id",
            "name",
        )
        read_only_fields = ("id",)
