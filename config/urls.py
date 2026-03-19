from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from accounts.views import CustomPasswordChangeView, htmx_email_test, profile as account_profile

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/profile/", account_profile, name="account_profile"),
    path("accounts/password/change/", CustomPasswordChangeView.as_view(), name="password_change"),
    path("htmx/accounts/email-test/", htmx_email_test, name="htmx_email_test"),
    path("", include("dashboard.urls")),
]
