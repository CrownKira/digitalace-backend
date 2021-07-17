from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_bulk.routes import BulkRouter

from customer import views


bulk_router = BulkRouter()
bulk_router.register("invoices", views.InvoiceViewSet)
bulk_router.register("credit_notes", views.CreditNoteViewSet)
bulk_router.register("customers", views.CustomerViewSet)
bulk_router.register("sales_orders", views.SalesOrderViewSet)


router = DefaultRouter()
router.register("credits_applications", views.CreditsApplicationViewSet)

app_name = "customer"

urlpatterns = [
    path("", include(router.urls)),
    path("", include(bulk_router.urls)),
]
