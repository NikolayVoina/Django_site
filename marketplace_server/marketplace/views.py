from django.contrib.auth.views import TemplateView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from products.models import Category, Product
from products.utils import daily_special_timer


def handler_404(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(request, "errors/404.html")


def handler_500(request: HttpRequest) -> HttpResponse:
    return render(request, "errors/500.html")


class IndexTemplateView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()

        daily_special_product = Product.get_daily_special()
        daily_special_product_price = daily_special_product.product_item.price / 2 if daily_special_product else None
        context.update(
            {
                "preferred_categories": Category.objects.filter(is_preferred=True)[:3],
                "categories": categories,
                "popular_products": Product.get_popular_products(),
                "limited_products": Product.get_limited_products(),

                "daily_special_product": daily_special_product,
                "daily_special_product_price": daily_special_product_price,
                "daily_special_timer": daily_special_timer(),
            }
        )
        return context
