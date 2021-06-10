from decimal import Decimal
import os

from django.db import models

from .user import get_unique_filename


def product_image_file_path(instance, filename):
    """Generate file path for new product image"""
    return os.path.join(
        "uploads/product/images/", get_unique_filename(filename)
    )


def product_thumbnail_file_path(instance, filename):
    """Generate file path for new product thumbnail"""
    return os.path.join(
        "uploads/product/thumbnails/", get_unique_filename(filename)
    )


def category_image_file_path(instance, filename):
    """Generate file path for new category image"""
    return os.path.join(
        "uploads/category/thumbnails/", get_unique_filename(filename)
    )


def customer_image_file_path(instance, filename):
    """Generate file path for new customer image"""
    return os.path.join(
        "uploads/customer/images/", get_unique_filename(filename)
    )


def supplier_image_file_path(instance, filename):
    """Generate file path for new supplier image"""
    return os.path.join(
        "uploads/supplier/images/", get_unique_filename(filename)
    )


class Customer(models.Model):
    """Customer managed by a company"""

    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    agent = models.ManyToManyField("User", blank=True)
    attention = models.CharField(max_length=255, blank=True)

    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    zipcode = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=255, blank=True)
    term = models.CharField(max_length=255, blank=True)
    phone_no = models.CharField(max_length=255, blank=True)

    email = models.EmailField(max_length=255, blank=True)
    receivables = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, default=Decimal("0.00")
    )
    first_seen = models.DateField(null=True, blank=True)
    last_seen = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to=customer_image_file_path, blank=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """Supplier managed by a company"""

    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    agent = models.ManyToManyField("User", blank=True)
    attention = models.CharField(max_length=255, blank=True)

    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    zipcode = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=255, blank=True)
    term = models.CharField(max_length=255, blank=True)
    phone_no = models.CharField(max_length=255, blank=True)

    email = models.EmailField(max_length=255, blank=True)
    payables = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, default=Decimal("0.00")
    )
    first_seen = models.DateField(null=True, blank=True)
    last_seen = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to=supplier_image_file_path, blank=True)

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    """Category of a product"""

    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    agent = models.ManyToManyField("User", blank=True)

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to=category_image_file_path, blank=True)

    class Meta:
        verbose_name_plural = "product categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product managed by a company"""

    category = models.ForeignKey("ProductCategory", on_delete=models.CASCADE)
    # TODO: mandatory?
    supplier = models.ForeignKey("Supplier", on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    # TODO: create a class for unit
    unit = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    image = models.ImageField(upload_to=product_image_file_path, blank=True)
    thumbnail = models.ImageField(
        upload_to=product_thumbnail_file_path, blank=True
    )
    stock = models.IntegerField(blank=True, default=0)
    sales = models.IntegerField(blank=True, default=0)

    def __str__(self):
        return self.name


class StockBalance(models.Model):
    """Stock balance of a product"""

    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity_in = models.IntegerField()
    quantity_out = models.IntegerField()
    balance = models.IntegerField()
    period = models.CharField(max_length=255)

    def __str__(self):
        return self.product + " (" + self.period + ")"


class Payslip(models.Model):
    """Payslip managed by a company"""

    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey("Company", on_delete=models.CASCADE)

    date = models.DateField()
    year = models.CharField(max_length=255)
    month = models.CharField(max_length=255)
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    total_allowances = models.DecimalField(max_digits=10, decimal_places=2)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amt = models.DecimalField(max_digits=10, decimal_places=2)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=255)
    bank = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
