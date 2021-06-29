from django.urls import path, include

from rest_framework.routers import DefaultRouter

from company import views


router = DefaultRouter()
router.register("users", views.ListUserViewSet)
router.register("categories", views.ProductCategoryViewSet)
router.register("products", views.ProductViewSet)
router.register("payment_methods", views.PaymentMethodViewSet)
router.register("payslips", views.PayslipViewSet)
router.register("roles", views.RoleViewSet)
router.register("departments", views.DepartmentViewSet)
router.register("designations", views.DesignationViewSet)
router.register("employees", views.EmployeeViewSet)


app_name = "company"

urlpatterns = [path("", include(router.urls))]
