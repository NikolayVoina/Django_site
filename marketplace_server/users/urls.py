from allauth.account.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.urls import path

from users.views import (
    MarketplaceLoginView,
    MarketplacePasswordResetDoneView,
    MarketplacePasswordResetView,
    MarketplaceProfileView,
    MarketplaceSignupView,
    ResendEmailVerification,
)

app_name = "users"

urlpatterns = [
    path("signup/", MarketplaceSignupView.as_view(), name="signup"),
    path("login/", MarketplaceLoginView.as_view(), name="login"),
    path("profile/", MarketplaceProfileView.as_view(), name="profile"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password/reset/", MarketplacePasswordResetView.as_view(), name="forgot_password"),
    path("password/reset/done/", MarketplacePasswordResetDoneView.as_view(), name="forgot_password_done"),
    path(
        "profile/resend-verfication/",
        login_required(ResendEmailVerification.as_view()),
        name="resend_email_verification"
    ),
]
