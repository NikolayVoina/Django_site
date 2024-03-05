from django.http import HttpRequest

from products.utils import Comparison


def comparison(request: HttpRequest) -> dict:
    return {"comparison": Comparison(request)}
