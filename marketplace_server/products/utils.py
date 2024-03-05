import datetime
from collections import defaultdict
from typing import TYPE_CHECKING, Optional

import croniter
from django.conf import settings
from django.db.models import Q
from django.http import HttpRequest
from django.utils import timezone

if TYPE_CHECKING:
    from orders.cart import Cart
    from products.models import Discount, Product, ProductItem


def daily_special_timer() -> dict:
    now = timezone.now()
    cron_schedule = "0 2 * * *"
    cron = croniter.croniter(cron_schedule, now)
    next_run_time = cron.get_next(datetime.datetime)
    return next_run_time


class _AbsDiscountManager:

    def __init__(self) -> None:
        self.discount = None

    @property
    def original_price(self) -> float:
        return NotImplemented

    def process(self) -> float:
        from products.models import Discount

        handlers = {
            Discount.PERCENT: self._apply_percent_discount,
            Discount.FIXED_AMOUNT: self._apply_fixed_amount_discount,
            Discount.FIXED_PRICE: self._apply_fixed_price_discount,
        }

        if self._get_discount():
            return handlers[self.discount.discount_method](self.original_price)

    def _get_discount(self) -> Optional["Discount"]:
        return NotImplemented

    def _apply_percent_discount(self, original_price: float) -> float:
        discount_amount = (original_price * self.discount.value) / 100
        discounted_price = original_price - discount_amount
        return float(discounted_price)

    def _apply_fixed_amount_discount(self, original_price: float) -> float:
        discounted_price = max(original_price - self.discount.value, 1)
        return float(discounted_price)

    def _apply_fixed_price_discount(self, original_price: float) -> float:
        return float(self.discount.value)


class DiscountManager(_AbsDiscountManager):

    def __init__(self, product_item: "ProductItem") -> None:
        super().__init__()
        self.product_item = product_item

    @property
    def original_price(self) -> float:
        return self.product_item.price

    def _get_discount(self) -> Optional["Discount"]:
        active_product_discount = self.product_item.product.discounts.filter(
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now()
        ).order_by("-priority").first()

        active_category_discount = self.product_item.product.category.discounts.filter(
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now()
        ).order_by("-priority").first()

        self.discount = active_category_discount or active_product_discount
        return self.discount


class DiscountCartManager(_AbsDiscountManager):

    def __init__(self, cart: "Cart") -> None:
        super().__init__()
        self.cart = cart

    @property
    def original_price(self) -> float:
        return self.cart.get_total_original_price()

    def _get_discount(self) -> Optional["Discount"]:
        from products.models import CartDiscount

        q_empty_filter = Q(min_items__isnull=True, max_items__isnull=True, min_total_price__isnull=True,
                           max_total_price__isnull=True)
        q_items_filter = Q(
            min_items__isnull=False, max_items__isnull=False,
            min_items__lte=len(self.cart), max_items__gte=len(self.cart)
        )
        q_total_price_filter = Q(
            min_total_price__isnull=False, max_total_price__isnull=False,
            min_total_price__lte=self.original_price, max_total_price__gte=self.original_price
        )

        active_discount = CartDiscount.objects.filter(
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now()
        ).filter(
            q_empty_filter | q_items_filter | q_total_price_filter
        ).order_by("-priority").first()

        self.discount = active_discount
        return self.discount


class Comparison:
    def __init__(self, request: HttpRequest):
        self.session = request.session
        self.comparison = request.session.get(settings.COMPARISON_SESSION_KEY)
        if not self.comparison:
            self.comparison = self.session[settings.COMPARISON_SESSION_KEY] = {}

    def __iter__(self):
        yield from self.comparison.values()

    def __len__(self):
        return len(self.comparison)

    def add(self, product: "Product") -> None:
        product_id = str(product.pk)
        if product_id not in self.comparison:
            self.comparison[product_id] = {
                "pk": product.pk,
                "title": product.title,
                "category": product.category.title,
                "characteristics": product.characteristics,
                "price": str(product.product_item.price),
                "preview": product.preview,
            }
            self.comparison["differing_characteristics"] = self.get_differing_characteristics()
            self.save()

    def remove(self, product: "Product") -> None:
        product_id = str(product.pk)
        if product_id in self.comparison:
            del self.comparison[product_id]
            if len(self.comparison) < 3:
                self.comparison = self.session[settings.COMPARISON_SESSION_KEY] = {}
            self.save()

    def save(self) -> None:
        self.session.modified = True

    def clear(self) -> None:
        del self.session[settings.COMPARISON_SESSION_KEY]
        self.save()

    def get_differing_characteristics(self) -> list:
        differing_characteristics = defaultdict(set)
        for item, item_value in self.comparison.items():
            if item == "differing_characteristics":
                continue
            for key, value in item_value["characteristics"].items():
                if isinstance(value, list):
                    value = ", ".join(value)
                differing_characteristics[key].add(value)
        return [k for k, v in differing_characteristics.items() if len(v) > 1]


def same_page_url(request: HttpRequest, redirect_url: str) -> str:
    http_referer = request.META.get("HTTP_REFERER")
    return http_referer if http_referer else redirect_url
