from django.db import models
from django.db.models.deletion import SET_NULL
from django.utils.translation import gettext_lazy as _


class Document(models.Model):
    """
    Commercial document used to records
    a transaction between a buyer and a seller
    """

    class DeliveryStatus(models.TextChoices):
        COMPLETED = "CP", _("Completed")
        PENDING = "PD", _("Pending")
        CANCELLED = "CC", _("Cancelled")

    class PaymentStatus(models.TextChoices):
        PAID = "PD", _("Paid")
        UNPAID = "UPD", _("Unpaid")

    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    reference = models.CharField(max_length=255)

    date = models.DateField()
    description = models.TextField(blank=True)
    payment_date = models.DateField(null=True, blank=True)
    # create a class for payment_method
    payment_method = models.CharField(max_length=255, blank=True)
    payment_note = models.TextField(blank=True)
    gst_rate = models.DecimalField(max_digits=10, decimal_places=2)
    discount_rate = models.DecimalField(max_digits=10, decimal_places=2)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    net = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        # https://docs.djangoproject.com/en/3.2/topics/db/models/#abstract-base-classes
        abstract = True


class LineItem(models.Model):
    """Line item in a document"""

    # warn the user before deleting the product
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    # TODO: create a class for unit
    unit = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

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
    sales_order = models.OneToOneField(
        "SalesOrder", on_delete=SET_NULL, null=True, blank=True
    )
    status = models.CharField(
        max_length=3,
        blank=True,
        choices=Document.PaymentStatus.choices,
        default=Document.PaymentStatus.UNPAID,
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
    status = models.CharField(
        max_length=3,
        blank=True,
        choices=Document.DeliveryStatus.choices,
        default=Document.DeliveryStatus.PENDING,
    )


class SalesOrderItem(LineItem):
    """Line item in a sales order"""

    sales_order = models.ForeignKey("SalesOrder", on_delete=models.CASCADE)


class Receive(Document):
    """Record of products received from a supplier"""

    supplier = models.ForeignKey(
        "Supplier", on_delete=models.SET_NULL, null=True
    )
    purchase_order = models.OneToOneField(
        "PurchaseOrder", on_delete=SET_NULL, null=True, blank=True
    )
    status = models.CharField(
        max_length=3,
        blank=True,
        choices=Document.PaymentStatus.choices,
        default=Document.PaymentStatus.UNPAID,
    )


class ReceiveItem(LineItem):
    """Line item in a receive"""

    receive = models.ForeignKey("Receive", on_delete=models.CASCADE)


class PurchaseOrder(Document):
    """Purchase order issued to a supplier"""

    supplier = models.ForeignKey(
        "Supplier", on_delete=models.SET_NULL, null=True
    )
    status = models.CharField(
        max_length=3,
        blank=True,
        choices=Document.DeliveryStatus.choices,
        default=Document.DeliveryStatus.PENDING,
    )


class PurchaseOrderItem(LineItem):
    """Line item in a purchase order"""

    purchase_order = models.ForeignKey(
        "PurchaseOrder", on_delete=models.CASCADE
    )
