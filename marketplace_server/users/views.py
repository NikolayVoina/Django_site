from allauth.account.models import EmailAddress
from allauth.account.views import LoginView, PasswordResetDoneView, PasswordResetView, SignupView, View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import TemplateView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from users.forms import (
    MarketplaceLoginForm,
    MarketplaceProfileForm,
    MarketplaceResetPasswordForm,
    MarketplaceSignupForm,
)
from users.models import User


class EmailVerificationSuccessTemplateView(TemplateView):
    template_name = "email-verification-success.html"


class MarketplaceSignupView(SignupView):
    template_name = "users/registration.html"
    form_class = MarketplaceSignupForm


class MarketplaceLoginView(LoginView):
    template_name = "users/login.html"
    form_class = MarketplaceLoginForm


class ResendEmailVerification(View):
    def get(self, request: HttpRequest, *args, **kwargs):  # noqa: ANN201
        email_address = EmailAddress.objects.filter(user=request.user).first()
        messages.info(request, "Письмо повторно отправлено", extra_tags="email_resent")
        email_address.send_confirmation(request, True)
        return redirect("users:profile")


class MarketplaceProfileView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = User
    template_name = "users/profile.html"
    form_class = MarketplaceProfileForm
    login_url = reverse_lazy("users:login")
    success_url = reverse_lazy("users:profile")
    success_message = "Данные сохранены."

    def get_object(self, **kwargs) -> User:
        return self.request.user

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["view_history"] = self.get_object().get_history()
        context["orders"] = self.get_object().get_orders()
        return context


class MarketplacePasswordResetView(PasswordResetView):
    template_name = "users/password/forgot-password.html"
    form_class = MarketplaceResetPasswordForm
    success_url = reverse_lazy("users:forgot_password_done")


class MarketplacePasswordResetDoneView(PasswordResetDoneView):
    template_name = "users/password/forgot-password-confirmation.html"
