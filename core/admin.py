from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from core import models


class UserAdmin(BaseUserAdmin):
    ordering = ["id"]
    list_display = ["email", "name"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal Info"), {"fields": ("name",)}),
        (
            _("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser")},
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Company)
admin.site.register(models.Department)
admin.site.register(models.Role)
admin.site.register(models.UserConfig)
admin.site.register(models.Customer)
admin.site.register(models.Supplier)
admin.site.register(models.ProductCategory)
admin.site.register(models.Product)
admin.site.register(models.Payslip)
admin.site.register(models.Invoice)
admin.site.register(models.InvoiceItem)
admin.site.register(models.SalesOrder)
admin.site.register(models.SalesOrderItem)
admin.site.register(models.Receive)
admin.site.register(models.ReceiveItem)
admin.site.register(models.PurchaseOrder)
admin.site.register(models.PurchaseOrderItem)
