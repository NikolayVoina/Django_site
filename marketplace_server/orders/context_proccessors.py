from django.http import HttpRequest

from orders.cart import Cart


def cart(request: HttpRequest) -> dict:
    return {"cart": Cart(request)}