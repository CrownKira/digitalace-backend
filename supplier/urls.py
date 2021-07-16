from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_bulk.routes import BulkRouter

from supplier import views


router = DefaultRouter()
bulk_router = BulkRouter()

bulk_router.register("receives", views.ReceiveViewSet)
bulk_router.register("suppliers", views.SupplierViewSet)
bulk_router.register("purchase_orders", views.PurchaseOrderViewSet)

app_name = "supplier"

urlpatterns = [
    path("", include(router.urls)),
    path("", include(bulk_router.urls)),
]
