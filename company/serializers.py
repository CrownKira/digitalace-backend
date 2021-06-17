from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from core.models import (
    Product,
    ProductCategory,
    Payslip,
    Role,
    Department,
    Designation,
    Customer,
    User,
)
from user.serializers import UserSerializer


# TODO: create an abstract class for get_image logic
# https://stackoverflow.com/questions/33137165/django-rest-framework-abstract-class-serializer
class ProductCategorySerializer(serializers.ModelSerializer):
    """Serializer for product category objects"""

    class Meta:
        model = ProductCategory
        fields = (
            "id",
            # "company",
            "name",
            "image",
        )
        read_only_fields = ("id",)
        extra_kwargs = {"image": {"allow_null": True}}

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
            "description",
        )
        read_only_fields = ("id",)
        extra_kwargs = {
            "image": {
                "allow_null": True
            },  # TODO: remove allow_null (should only allow "")
            "thumbnail": {"allow_null": True},
        }

    def get_fields(self):
        fields = super().get_fields()
        if self.context["request"].method in ["GET"]:
            fields["image"] = serializers.SerializerMethodField()
            fields["thumbnail"] = serializers.SerializerMethodField()
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
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 5},
            "image": {"allow_null": True},
        }

    def get_fields(self):
        fields = super().get_fields()
        if self.context["request"].method in ["GET"]:
            fields["resume"] = serializers.SerializerMethodField()
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


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for role objects"""

    class Meta:
        model = Role
        fields = ("id", "name", "image", "permissions")
        read_only_fields = ("id",)
        extra_kwargs = {"image": {"allow_null": True}}

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

    def validate(self, attrs):
        name = attrs.get("name")
        company = self.context["request"].user.company
        if self.context["request"].method in ["POST"]:
            if Role.objects.filter(company=company, name=name).exists():
                msg = _("A role with this name already exists")
                raise serializers.ValidationError(msg)
        elif (
            Role.objects.exclude(pk=self.instance.pk)
            .filter(company=company, name=name)
            .exists()
        ):
            msg = _("A role with this name already exists")
            raise serializers.ValidationError(msg)

        return attrs


class DesignationSerializer(serializers.ModelSerializer):
    """Serializer for designation objects"""

    class Meta:
        model = Designation
        fields = ("id", "name", "user_set")
        read_only_fields = ("id",)

    def get_fields(self):
        fields = super().get_fields()

        fields["user_set"] = serializers.PrimaryKeyRelatedField(
            many=True,
            queryset=User.objects.filter(
                is_staff=False,
                company=self.context["request"].user.company,
            ).distinct(),
        )
        return fields


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for department objects"""

    # If a nested representation may optionally accept the None value
    # you should pass the required=False flag to the nested serializer.
    # https://www.django-rest-framework.org/api-guide/serializers/#dealing-with-nested-objects
    designation_set = DesignationSerializer(many=True)

    class Meta:
        model = Department
        fields = ("id", "name", "image", "designation_set")
        read_only_fields = ("id",)
        extra_kwargs = {"image": {"allow_null": True}}

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

    # TODO: create a function to verify existence of name logic
    def validate(self, attrs):
        # TODO: check for uniqueness of designation names
        name = attrs.get("name")
        company = self.context["request"].user.company
        if self.context["request"].method in ["POST"]:
            if Department.objects.filter(company=company, name=name).exists():
                msg = _("A department with this name already exists")
                raise serializers.ValidationError(msg)
        elif (
            Department.objects.exclude(pk=self.instance.pk)
            .filter(company=company, name=name)
            .exists()
        ):
            msg = _("A department with this name already exists")
            raise serializers.ValidationError(msg)

        return attrs

    # TODO: make this a global function
    def update_delete_or_create(self, instance, designations_data):
        designation_set = instance.designation_set.all()
        designations_data_count = len(designations_data)
        designation_set_count = designation_set.count()
        total = max(designations_data_count, designation_set_count)
        delete_pks = []

        # TODO: add company to instance of serializer? eg. self._company?
        for i in range(total):
            if i < designation_set_count:
                designation = designation_set[i]
                designation_pk = designation.pk
                if i < designations_data_count:
                    designation_data = designations_data[i]
                    # TODO: better way to filter out id and pk?
                    designation_data.pop("id", None)
                    designation_data.pop("pk", None)
                    user_set = designation_data.pop("user_set")
                    designation.user_set.set(user_set)
                    # https://docs.djangoproject.com/en/3.2/ref/models/querysets/#update
                    Designation.objects.filter(pk=designation_pk).update(
                        **designation_data
                    )

                else:
                    # can't delete here since that will mutate the queryset
                    delete_pks.append(designation_pk)
            else:
                # add extra to db
                designation_data = designations_data[i]
                designation_data.pop("id", None)
                designation_data.pop("pk", None)
                user_set = designation_data.pop("user_set")
                designation = Designation.objects.create(
                    department=instance, **designation_data
                )
                designation.user_set.set(user_set)

        for delete_pk in delete_pks:
            Designation.objects.get(pk=delete_pk).delete()

    def create(self, validated_data):
        designations_data = validated_data.pop("designation_set", [])
        department = Department.objects.create(**validated_data)
        for designation_data in designations_data:
            user_set = designation_data.pop("user_set", [])
            designation = Designation.objects.create(
                department=department, **designation_data
            )
            designation.user_set.set(user_set)
        return department

    def update(self, instance, validated_data):
        designations_data = validated_data.pop("designation_set", [])
        self.update_delete_or_create(instance, designations_data)
        return super().update(instance, validated_data)
