from decimal import Decimal

from django.db import models
from django.db.models.deletion import SET_NULL


class Document(models.Model):
    """
    Commercial document used to records
    a transaction between a buyer and a seller
    """

    company = models.ForeignKey("Company", on_delete=models.CASCADE)

    date = models.DateField()
    description = models.TextField(blank=True)
    payment_date = models.DateField()
    # create a class for payment_method
    payment_method = models.CharField(max_length=255, blank=True)
    payment_note = models.TextField(blank=True)
    gst_rate = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0.00)
    )
    discount_rate = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0.00)
    )
    gst_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0.00)
    )
    discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0.00)
    )
    net = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0.00)
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0.00)
    )
    grand_total = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0.00)
    )

    class Meta:
        # https://docs.djangoproject.com/en/3.2/topics/db/models/#abstract-base-classes
        abstract = True


class LineItem(models.Model):
    """Line item in a document"""

    # warn the user before deleting the product
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    # TODO: create a class for unit
    unit = models.CharField(max_length=255)
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0.00)
    )
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0.00)
    )
    quantity = models.IntegerField()
    unit_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal(0.00)
    )

    class Meta:
        abstract = True


class Invoice(Document):
    """Invoice issued to a customer"""

    # https://stackoverflow.com/questions/38388423/what-does-on-delete-do-on-django-models
    # create a anonymous customer on sign up
    # when a customer is deleted, say the invoices
    # are created by anonymous (or deleted) customer.
    # but customer cannot be left blank on creation of the invoice
    customer = models.ForeignKey(
        "Customer", on_delete=models.SET_NULL, null=True
    )
    salesperson = models.ForeignKey(
        "User", on_delete=models.SET_NULL, null=True, blank=True
    )


class InvoiceItem(LineItem):
    """Line item in an invoice"""

    invoice = models.ForeignKey("Invoice", on_delete=models.CASCADE)


class SalesOrder(Document):
    """Sales order issued to a customer"""

    customer = models.ForeignKey(
        "Customer", on_delete=models.SET_NULL, null=True
    )
    salesperson = models.ForeignKey(
        "User", on_delete=models.SET_NULL, null=True, blank=True
    )
    # can be linked to existing or non-existing invoice
    invoice = models.OneToOneField(
        "Invoice", on_delete=SET_NULL, null=True, blank=True
    )


class SalesOrderItem(LineItem):
    """Line item in a sales order"""

    invoice = models.ForeignKey("SalesOrder", on_delete=models.CASCADE)
