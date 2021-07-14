from django.db import models
from django.db.models.deletion import SET_NULL
from django.utils.translation import gettext_lazy as _


class Document(models.Model):
    """
    Commercial document used to records
    a transaction between a buyer and a seller
    """

    company = models.ForeignKey("Company", on_delete=models.CASCADE)
    reference = models.CharField(max_length=255)

    date = models.DateField()
    description = models.TextField(blank=True)
    # can't be blank since these are calculated fields
    # TODO: move calculation logic to Document manager
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

    def __str__(self):
        return self.reference


class LineItem(models.Model):
    """Line item in a document"""

    # warn the user before deleting the product
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    # TODO: remove unit since it is not editable
    unit = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        abstract = True


class PaymentMethod(models.Model):
    """Payment method in a company"""

    name = models.CharField(max_length=255)
    company = models.ForeignKey("Company", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class CreditsApplication(models.Model):
    """Credits Applied"""

    invoice = models.ForeignKey("Invoice", on_delete=models.PROTECT, null=True)
    credit_note = models.ForeignKey(
        "CreditNote", on_delete=models.PROTECT, null=True
    )
    amount_to_credit = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()


class Adjustment(models.Model):
    """Inventory Adjustment"""

    class Mode(models.TextChoices):
        INCREASE = "INC", _("Increase")
        DECREASE = "DEC", _("Decrease")

    class Status(models.TextChoices):
        DRAFT = "DFT", _("Draft")
        ADJUSTED = "ADJ", _("Adjusted")

    date = models.DateField()
    description = models.TextField(blank=True)
    reason = models.TextField(blank=True)
    mode = models.CharField(
        max_length=4,
        blank=True,
        choices=Mode.choices,
        default=Mode.INCREASE,
    )
    status = models.CharField(
        max_length=4,
        blank=True,
        choices=Status.choices,
        default=Status.DRAFT,
    )


class AdjustmentItem(models.Model):
    """Line item in an inventory adjustment"""

    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    unit = models.CharField(max_length=255)
    quantity = models.IntegerField()


class CreditNote(Document):
    """Credit Note issued to a customer"""

    class Status(models.TextChoices):
        DRAFT = "DFT", _("Draft")
        OPEN = "OP", _("Open")
        # TODO: change to closed when no credits left
        CLOSED = "CL", _("Closed")

    customer = models.ForeignKey(
        "Customer", on_delete=models.SET_NULL, null=True
    )
    salesperson = models.ForeignKey(
        "User", on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(
        max_length=4,
        blank=True,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    created_from = models.ForeignKey(
        "Invoice", on_delete=models.SET_NULL, null=True
    )
    credits_used = models.DecimalField(max_digits=10, decimal_places=2)
    refund = models.DecimalField(max_digits=10, decimal_places=2)
    credits_remaining = models.DecimalField(max_digits=10, decimal_places=2)


class CreditNoteItem(LineItem):
    """Line item in a credit note"""

    credit_note = models.ForeignKey("CreditNote", on_delete=models.CASCADE)


class DeliveryOrder(Document):
    """Delivery Order issued to a customer"""

    # editable hence recreating all the fields and not referencing them
    # all fields will not be precalculated but will take input from the client
    customer = models.ForeignKey(
        "Customer", on_delete=models.SET_NULL, null=True
    )
    salesperson = models.ForeignKey(
        "User", on_delete=models.SET_NULL, null=True, blank=True
    )
    sales_order = models.ForeignKey(
        "SalesOrder", on_delete=SET_NULL, null=True, blank=True
    )
    # set null on delete to keep a backup
    invoice = models.ForeignKey(
        "Invoice", on_delete=SET_NULL, null=True, blank=True
    )
    credits_applied = models.DecimalField(max_digits=10, decimal_places=2)


class Invoice(Document):
    """Invoice issued to a customer"""

    class Status(models.TextChoices):
        DRAFT = "DFT", _("Draft")
        PAID = "PD", _("Paid")
        UNPAID = "UPD", _("Unpaid")

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
    # TODO: if attached to a sales_order,
    # will only have access to items in the sales order
    sales_order = models.ForeignKey(
        "SalesOrder", on_delete=SET_NULL, null=True, blank=True
    )
    status = models.CharField(
        max_length=4,
        blank=True,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    credits_applied = models.DecimalField(max_digits=10, decimal_places=2)
    balance_due = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.ForeignKey(
        "PaymentMethod", on_delete=models.SET_NULL, null=True, blank=True
    )
    payment_note = models.TextField(blank=True)


class InvoiceItem(LineItem):
    """Line item in an invoice"""

    invoice = models.ForeignKey("Invoice", on_delete=models.CASCADE)


class SalesOrder(Document):
    """Sales order issued to a customer"""

    class Status(models.TextChoices):
        DRAFT = "DFT", _("Draft")
        COMPLETED = "CP", _("Completed")
        PENDING = "PNDG", _("Pending")
        CANCELLED = "CC", _("Cancelled")

    customer = models.ForeignKey(
        "Customer", on_delete=models.SET_NULL, null=True
    )
    salesperson = models.ForeignKey(
        "User", on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(
        max_length=4,
        blank=True,
        choices=Status.choices,
        default=Status.DRAFT,
    )


class SalesOrderItem(LineItem):
    """Line item in a sales order"""

    sales_order = models.ForeignKey("SalesOrder", on_delete=models.CASCADE)


class Receive(Document):
    """Record of products received from a supplier"""

    class Status(models.TextChoices):
        DRAFT = "DFT", _("Draft")
        PAID = "PD", _("Paid")
        UNPAID = "UPD", _("Unpaid")

    supplier = models.ForeignKey(
        "Supplier", on_delete=models.SET_NULL, null=True
    )
    # TODO: conver to ForeignKey
    purchase_order = models.OneToOneField(
        "PurchaseOrder", on_delete=SET_NULL, null=True, blank=True
    )
    status = models.CharField(
        max_length=4,
        blank=True,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.ForeignKey(
        "PaymentMethod", on_delete=models.SET_NULL, null=True, blank=True
    )
    payment_note = models.TextField(blank=True)


class ReceiveItem(LineItem):
    """Line item in a receive"""

    receive = models.ForeignKey("Receive", on_delete=models.CASCADE)


class PurchaseOrder(Document):
    """Purchase order issued to a supplier"""

    class Status(models.TextChoices):
        DRAFT = "DFT", _("Draft")
        COMPLETED = "CP", _("Completed")
        PENDING = "PNDG", _("Pending")
        CANCELLED = "CC", _("Cancelled")

    supplier = models.ForeignKey(
        "Supplier", on_delete=models.SET_NULL, null=True
    )
    status = models.CharField(
        max_length=4,
        blank=True,
        choices=Status.choices,
        default=Status.DRAFT,
    )


class PurchaseOrderItem(LineItem):
    """Line item in a purchase order"""

    purchase_order = models.ForeignKey(
        "PurchaseOrder", on_delete=models.CASCADE
    )
