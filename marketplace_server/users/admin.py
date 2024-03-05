from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User, ViewHistory


class ViewHistoryInline(admin.TabularInline):
    model = ViewHistory
    readonly_fields = ["product", "updated"]
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "is_active"]
    list_filter = ["email"]
    readonly_fields = ["last_login", "date_joined"]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "email", "password", "avatar", "last_login", "date_joined"
                ]
            }
        ),
        (
            "Personal info",
            {
                "fields": [
                    "first_name", "last_name"
                ]
            }
        ),
        (
            "Delivery info",
            {
                "fields": [
                    "city", "address", "phone_number"
                ]
            }
        ),
        (
            "Permissions",
            {
                "fields": [
                    "is_staff", "is_superuser"
                ]
            }
        ),
    ]
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["-id",]
    filter_horizontal = []
    inlines = [
        ViewHistoryInline,
    ]

