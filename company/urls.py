from django.urls import path, include
from rest_framework.routers import DefaultRouter

from company import views


router = DefaultRouter()
router.register('products', views.ProductViewSet)

app_name = 'company'

urlpatterns = [
    path('', include(router.urls))
]
