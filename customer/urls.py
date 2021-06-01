from django.urls import path, include
from rest_framework.routers import DefaultRouter

from customer import views


router = DefaultRouter()
router.register('invoices', views.InvoiceViewSet)

app_name = 'customer'

urlpatterns = [
    path('', include(router.urls))
]
