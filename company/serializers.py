from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
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
    PaymentMethod,
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
            "name",
            "image",
        )
        read_only_fields = ("id",)
        # Please keep in mind that, if the field has already been
        # explicitly declared on the serializer class, then
        # the extra_kwargs option will be ignored.
        # https://www.django-rest-framework.org/api-guide/serializers/#additional-keyword-arguments
        extra_kwargs = {"image": {"allow_null": True}}

    def get_fields(self):
        fields = super().get_fields()

        try:
            if self.context["request"].method in ["GET"]:
                fields["image"] = serializers.SerializerMethodField()
        except KeyError:
            pass

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
            "reference",
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

        try:
            if self.context["request"].method in ["GET"]:
                fields["image"] = serializers.SerializerMethodField()
                fields["thumbnail"] = serializers.SerializerMethodField()
        except KeyError:
            pass

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

    def validate_reference(self, reference):
        company = self.context["request"].user.company

        if self.context["request"].method in ["POST"]:
            if Product.objects.filter(
                category__company=company, reference=reference
            ).exists():
                msg = _("A product with this reference already exists")
                raise serializers.ValidationError(msg)
        elif (
            Product.objects.exclude(pk=self.instance.pk)
            .filter(category__company=company, reference=reference)
            .exists()
        ):
            msg = _("A product with this reference already exists")
            raise serializers.ValidationError(msg)

        return reference


class PaymentMethodSerializer(serializers.ModelSerializer):
    """Serializer for payment method objects"""

    class Meta:
        model = PaymentMethod
        fields = (
            "id",
            "name",
        )


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
            "email",
            "name",
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
            "designation",
        )

        read_only_fields = ("id",)
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 5},
            "image": {"allow_null": True},
        }

    def get_fields(self):
        fields = super().get_fields()

        fields["department"] = serializers.SerializerMethodField(
            read_only=True
        )

        try:
            if self.context["request"].method in ["GET"]:
                fields["image"] = serializers.SerializerMethodField()
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
        except KeyError:
            pass

        return fields

    def get_department(self, obj):
        return (
            (
                obj.designation.department.pk
                if obj.designation.department
                else None
            )
            if obj.designation
            else None
        )

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        roles = validated_data.pop("roles")
        customer_set = validated_data.pop("customer_set")
        product_set = validated_data.pop("product_set")
        user = super().create(validated_data)
        user.roles.set(roles)
        user.customer_set.set(customer_set)
        user.product_set.set(product_set)
        return user


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for role objects"""

    class Meta:
        model = Role
        fields = ("id", "name", "image")
        read_only_fields = ("id",)
        extra_kwargs = {"image": {"allow_null": True}}

    def get_fields(self):
        fields = super().get_fields()

        fields["permissions"] = serializers.PrimaryKeyRelatedField(
            many=True, queryset=Permission.objects.filter(pk__gte=29)
        )

        try:
            if self.context["request"].method in ["GET"]:
                fields["image"] = serializers.SerializerMethodField()
            fields["user_set"] = serializers.PrimaryKeyRelatedField(
                many=True,
                queryset=get_user_model()
                .objects.filter(
                    is_staff=False,
                    company=self.context["request"].user.company,
                )
                .distinct(),
            )
        except KeyError:
            pass

        return fields

    def get_image(self, obj):
        return {
            "src": obj.image.url if obj.image else "",
            "title": obj.image.name if obj.image else "",
        }

    def validate_name(self, name):
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

        return name


class DesignationSerializer(serializers.ModelSerializer):
    """Serializer for designation objects"""

    class Meta:
        model = Designation
        fields = ("id", "department", "name", "user_set")
        read_only_fields = ("id", "department")

    def get_fields(self):
        fields = super().get_fields()

        try:
            fields["user_set"] = serializers.PrimaryKeyRelatedField(
                many=True,
                queryset=get_user_model()
                .objects.filter(
                    is_staff=False,
                    company=self.context["request"].user.company,
                )
                .distinct(),
            )
        except KeyError:
            pass

        return fields


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for department objects"""

    # If a nested representation may optionally accept the None value
    # you should pass the required=False flag to the nested serializer.
    # https://www.django-rest-framework.org/api-guide/serializers/#dealing-with-nested-objects

    # https://github.com/encode/django-rest-framework/issues/7262
    # TL;DR: No, DRF doesn't support nested writable
    # serializers with multipart/form-data
    # Nested serializers that are flagged many=True are not working
    # with multipart/form-data mostly because there's no standard notation
    # about how a field name should looks like.
    # I, once, worked on it but got burnt out and lost that work.
    # Most of the work to do should be within
    # https://github.com/encode/django-rest-framework/blob/master/rest_framework/utils/html.py

    class Meta:
        model = Department
        fields = ("id", "name", "image")
        read_only_fields = ("id",)
        extra_kwargs = {"image": {"allow_null": True}}

    def get_fields(self):
        fields = super().get_fields()

        fields["designation_set"] = DesignationSerializer(
            many=True,
            # required is set to false since get_value()
            # returns empty for multipart data
            # https://github.com/encode/django-rest-framework/blob/master/rest_framework/serializers.py#L474
            required=False,
        )
        try:
            if self.context["request"].method in ["GET"]:
                fields["image"] = serializers.SerializerMethodField()
        except KeyError:
            pass

        return fields

    def get_image(self, obj):
        return {
            "src": obj.image.url if obj.image else "",
            "title": obj.image.name if obj.image else "",
        }

    def _validate_multipart_designation_set(self, designation_set):
        if not isinstance(designation_set, list):
            ValidationError(_("designation_set expects a list"))

        validated_data = []
        for item in designation_set:
            serializer = DesignationSerializer(data=item)
            serializer.is_valid(raise_exception=True)
            validated_data.append(serializer.validated_data)

        return validated_data

    def validate_name(self, name):
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

        return name

    # TODO: create a function to verify existence of name logic
    def validate(self, attrs):
        # TODO: check for uniqueness of designation names
        # FIXME: designation_set not in attrs for multipart data
        if "designation_set" not in attrs:
            # serializer checks for existence of designation_set
            # for some reason even if it is not writable for multipart data
            # https://stackoverflow.com/questions/39565023/django-querydict-only-returns-the-last-value-of-a-list
            designation_set = self.initial_data.getlist("designation_set")
            attrs[
                "designation_set"
            ] = self._validate_multipart_designation_set(designation_set)

        return attrs

    # TODO: make this a global function
    def _update_delete_or_create(self, instance, designations_data):
        designation_instances = instance.designation_set.all()
        designation_set_count = designation_instances.count()
        bulk_updates = []
        bulk_creates = []
        user_set_creates = []

        # this loop does not evaluate designation_instances
        # TODO: test other approach: iterate over designation
        # instances, update and delete in the loop. bulk create
        # the rest after exiting the loop
        for i, designation_data in enumerate(designations_data):
            designation_data.pop("id", None)
            designation_data.pop("pk", None)
            user_set = designation_data.pop("user_set")
            if i < designation_set_count:
                # update
                designation_instance = designation_instances[i]
                designation_instance.user_set.set(user_set)
                for attr, value in designation_data.items():
                    setattr(designation_instance, attr, value)
                bulk_updates.append(designation_instance)
            else:
                # create
                user_set_creates.append(user_set)
                bulk_creates.append(
                    # unpack first to prevent overriding
                    Designation(
                        **designation_data,
                        department=instance,
                    )
                )

        Designation.objects.bulk_update(bulk_updates, ["name"])
        # delete
        Designation.objects.filter(department=instance).exclude(
            pk__in=[obj.pk for obj in bulk_updates]
        ).delete()
        # new_designations are in order of bulk_creates
        new_designations = Designation.objects.bulk_create(bulk_creates)

        for i, new_designation in enumerate(new_designations):
            new_designation.user_set.set(user_set_creates[i])

    def create(self, validated_data):
        designations_data = validated_data.pop("designation_set", [])
        department = Department.objects.create(**validated_data)
        for designation_data in designations_data:
            user_set = designation_data.pop("user_set", [])
            designation_instance = Designation.objects.create(
                **designation_data, department=department
            )
            designation_instance.user_set.set(user_set)
        return department

    def update(self, instance, validated_data):
        designations_data = validated_data.pop("designation_set", [])
        self._update_delete_or_create(instance, designations_data)
        return super().update(instance, validated_data)
