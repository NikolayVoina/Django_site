from django.contrib import admin

from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ("order", "product_item", "quantity", "price")
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "payment_method", "updated_at", "created_at")
    list_filter = ("updated_at",)
    readonly_fields = ("updated_at", "created_at")
    search_fields = ("user", "status", "payment_method", "updated_at")
    ordering = ("-id",)
    inlines = (OrderItemInline,)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "user", "status", "delivery_info", "payment_method", ("updated_at", "created_at"),
                )
            }
        ),
    )
