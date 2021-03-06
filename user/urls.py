from django.urls import path

from user import views


app_name = "user"

urlpatterns = [
    path("create/", views.CreateOwnerView.as_view(), name="create"),
    path("token/", views.CreateTokenView.as_view(), name="token"),
    path("me/", views.ManageProfileView.as_view(), name="me"),
    path("config/", views.UserConfigView.as_view(), name="config"),
]
