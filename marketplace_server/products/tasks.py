import random

from celery import shared_task

from products.models import Product


@shared_task
def product_is_daily_special() -> dict:
    result = {"prev_daily_special_product": None, "new_daily_special_product": None}
    daily_special_product = Product.get_daily_special()

    if daily_special_product:
        result["prev_daily_special_product"] = daily_special_product.id
        daily_special_product.is_daily_special = False
        daily_special_product.save()

    limited_edition_products = Product.objects.filter(is_limited_edition=True)

    random_limited_product = random.choice(limited_edition_products)
    random_limited_product.is_daily_special = True
    random_limited_product.save()

    result["new_daily_special_product"] = random_limited_product.id

    return result
