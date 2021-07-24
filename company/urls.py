from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_bulk.routes import BulkRouter


from company import views


router = DefaultRouter()
bulk_router = BulkRouter()

bulk_router.register("users", views.ListUserViewSet)
bulk_router.register("categories", views.ProductCategoryViewSet)
bulk_router.register("products", views.ProductViewSet)
bulk_router.register("payment_methods", views.PaymentMethodViewSet)
bulk_router.register("payslips", views.PayslipViewSet)
bulk_router.register("roles", views.RoleViewSet)
bulk_router.register("departments", views.DepartmentViewSet)
bulk_router.register("designations", views.DesignationViewSet)
bulk_router.register("employees", views.EmployeeViewSet)
bulk_router.register("adjustments", views.AdjustmentViewSet)
bulk_router.register("announcements", views.AnnouncementViewSet)


app_name = "company"

urlpatterns = [
    path("", include(router.urls)),
    path("", include(bulk_router.urls)),
]
