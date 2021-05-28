from django.db import models


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
    # TODO: mandatory?
    supplier = models.ForeignKey("Supplier", on_delete=models.CASCADE)

    name = models.CharField(max_length=255)
    # TODO: create a class for unit
    unit = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


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
