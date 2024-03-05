from decimal import Decimal

from django.db import models
from django.db.models import QuerySet


class Order(models.Model):
    CREATED = "created"
    PAID = "paid"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    STATUSES = [
        (CREATED, "Сформирован"),
        (PAID, "Оплачен"),
        (IN_TRANSIT, "В пути"),
        (COMPLETED, "Доставлен"),
    ]

    BY_CARD = "by_card"
    BY_CASH = "by_cash"
    PAYMENT_METHODS = [
        (BY_CARD, "Картой"),
        (BY_CASH, "Наличными"),
    ]

    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=STATUSES, default=CREATED)
    delivery_info = models.JSONField(default=dict, null=True, blank=True)
    payment_method = models.CharField(choices=PAYMENT_METHODS, null=True, blank=True)

    @property
    def product_items(self) -> QuerySet:
        return OrderItem.objects.filter(order=self.pk)

    @property
    def total_price(self) -> float:
        return sum([item.total_price for item in self.product_items])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_item = models.ForeignKey("products.ProductItem", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self) -> Decimal:
        return self.quantity * self.price
