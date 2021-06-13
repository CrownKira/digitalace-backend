from django.urls import path, include
from rest_framework.routers import DefaultRouter

from company import views


router = DefaultRouter()
router.register("categories", views.ProductCategoryViewSet)
router.register("products", views.ProductViewSet)
router.register("payslips", views.PayslipViewset)
router.register("roles", views.RoleViewSet)
router.register("departments", views.DepartmentViewSet)
router.register("employees", views.DepartmentViewSet)

app_name = "company"

urlpatterns = [path("", include(router.urls))]
