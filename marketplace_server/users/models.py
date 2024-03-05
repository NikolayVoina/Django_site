from __future__ import annotations

from typing import TYPE_CHECKING

from allauth.account.models import EmailAddress
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone

if TYPE_CHECKING:
    from products.models import Product


def user_avatar_path(instance: User, filename: str) -> str:
    return f"users/user_{instance.pk}/avatar/{filename}"


class UserManager(BaseUserManager):
    def _create_user(self, email: str, password: str = None, **extra_fields) -> User:
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str = None, **extra_fields) -> User:
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str = None, **extra_fields) -> User:
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(blank=True, unique=True)

    avatar = models.ImageField(null=True, upload_to=user_avatar_path, default=None)
    city = models.CharField(max_length=150, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=150, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    @property
    def is_email_verified(self) -> bool:
        email_address = EmailAddress.objects.filter(user=self).first()
        return email_address.verified if email_address else False

    def get_history(self) -> QuerySet:
        return self.viewhistory_set.order_by("-updated")

    def add_view_history(self, product: Product) -> None:
        history_by_product, created = ViewHistory.objects.get_or_create(product=product, user=self)
        if history_by_product:
            history_by_product.updated = timezone.now()
            history_by_product.save()

        if self.get_history().count() > 20:
            self.get_history().last().delete()

    def get_orders(self) -> QuerySet:
        return self.order_set.order_by("-updated_at")

    def update_delivery_info(self, **kwargs) -> None:
        for arg in ("city", "address", "phone_number"):
            setattr(self, arg, kwargs[arg])
        self.save()


class ViewHistory(models.Model):
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Viewing {self.product} on the {self.updated}"
