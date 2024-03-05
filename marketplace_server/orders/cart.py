from django.conf import settings
from django.http import HttpRequest

from orders.models import Order, OrderItem
from products.models import ProductItem
from products.utils import DiscountCartManager


class Cart:

    def __init__(self, request: HttpRequest):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_KEY)
        if not cart:
            cart = self.session[settings.CART_SESSION_KEY] = {}
        self.cart = cart

    def __iter__(self):
        for item in self.cart.values():
            item["total_item_price"] = item["price"] * item["quantity"]
            if item["price_with_discount"]:
                item["total_item_discount_price"] = item["price_with_discount"] * item["quantity"]
            yield item

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def add(self, product_item: ProductItem) -> None:
        product_item_id = str(product_item.pk)
        if product_item_id not in self.cart:
            self.cart[product_item_id] = {
                "pk": product_item.pk,
                "product_id": product_item.product.id,
                "title": product_item.product.title,
                "description": product_item.product.description,
                "image": product_item.product.preview,
                "quantity": 1,
                "price": float(product_item.price),
                "price_with_discount": product_item.price_with_discount,
            }
        else:
            self.cart[product_item_id]["quantity"] += 1
        product_item.quantity -= 1
        product_item.save()
        self.save()

    def remove(self, product_item: ProductItem) -> None:
        product_item_id = str(product_item.pk)
        if product_item_id in self.cart:
            product_item.quantity += self.cart[product_item_id]["quantity"]
            product_item.save()
            del self.cart[product_item_id]
            self.save()

    def get_total_price(self) -> float:
        total_price = 0
        for item in self.cart.values():
            if item["price_with_discount"]:
                total_price += item["price_with_discount"] * item["quantity"]
            else:
                total_price += item["price"] * item["quantity"]
        return total_price

    def get_total_discount_price(self) -> float:
        return sum(item["price_with_discount"] * item["quantity"] for item in self.cart.values())

    def get_total_original_price(self) -> float:
        return sum(item["price"] * item["quantity"] for item in self.cart.values())

    def get_cart_price_with_discount(self) -> float:
        return DiscountCartManager(self).process()

    def get_difference_original_price_and_discount_price(self) -> float:
        return self.get_total_original_price() - self.get_cart_price_with_discount()

    def save(self) -> None:
        self.session.modified = True

    def clear(self) -> None:
        del self.session[settings.CART_SESSION_KEY]
        self.save()

    def copy_to_order(self, order: Order) -> None:
        for item in self.cart.values():
            OrderItem.objects.create(
                order=order,
                product_item_id=item["pk"],
                quantity=item["quantity"],
                price=item["price"],
            )
        self.clear()
