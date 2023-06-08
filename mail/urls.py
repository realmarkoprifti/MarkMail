from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from . import views


urlpatterns = [
    path("api/get/emails", views.get_emails),
    path("api/login", views.login),
    path("api/refresh/token", TokenRefreshView.as_view()),
    path("api/register", views.register),
    path("api/check/email", views.check_email),
    path("api/change/password", views.change_password),
    path("api/change/status", views.change_status),
    path("api/delete/email", views.delete_email),
    path("api/verify/rescue-code", views.verify_rescue_code),
    path("api/reset/password", views.reset_password),
    path('api/logout', TokenBlacklistView.as_view()),
    path("api/compose", views.compose_mail)
]