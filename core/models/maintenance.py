from decimal import Decimal

from django.db import models
from django.db.models.fields import CharField, DecimalField


class Customer(models.Model):
    """Customer managed by a company"""

    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    attention = models.ManyToManyField("User", blank=True)

    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    area = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=255, blank=True)
    term = models.CharField(max_length=255, blank=True)
    phone_no = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class Supplier(models.Model):
    """Supplier managed by a company"""

    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    attention = models.ManyToManyField("User", blank=True)

    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    area = models.CharField(max_length=255, blank=True)
    contact = models.CharField(max_length=255, blank=True)
    term = models.CharField(max_length=255, blank=True)
    phone_no = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    """Category of a product"""

    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    attention = models.ManyToManyField("User", blank=True)

    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "product categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    """Product managed by a company"""

    category = models.ForeignKey("ProductCategory", on_delete=models.CASCADE)
    supplier = models.ForeignKey("Supplier", on_delete=models.CASCADE)

    name = CharField(max_length=255)
    # TODO: create a class for unit
    unit = CharField(max_length=255)
    cost = DecimalField(max_digits=10, decimal_places=2, default=Decimal(0.00))
    unit_price = DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0.00)
    )

    def __str__(self):
        return self.name
