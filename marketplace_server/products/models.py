from __future__ import annotations

from django.db import models
from django.db.models import Avg, Min, QuerySet, Sum

from products.utils import DiscountManager
from users.models import User


def product_image_path(instance: ProductImage, filename: str) -> str:
    return f"products/product_{instance.product.pk}/images/{filename}"


class Category(models.Model):
    title = models.CharField(max_length=100)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_preferred = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title

    @property
    def lowest_price(self) -> str:
        return self.product_set.aggregate(lowest_price=Min("items__price")).get("lowest_price")


class Product(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    description = models.TextField(blank=True, null=True)
    characteristics = models.JSONField(blank=True, null=True)
    is_limited_edition = models.BooleanField(default=False)
    is_daily_special = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Product {self.title}"

    @classmethod
    def get_popular_products(cls) -> QuerySet:
        popular_products = cls.objects.exclude(review=None).annotate(review__rating=Avg("review__rating"))
        return popular_products.order_by("-review__rating")[:8]

    @classmethod
    def get_limited_products(cls) -> QuerySet:
        return cls.objects.filter(is_limited_edition=True)[:16]

    @classmethod
    def get_daily_special(cls) -> Product | None:
        return cls.objects.filter(is_daily_special=True).first()

    @property
    def product_item(self) -> ProductItem:
        return self.items.order_by("price").first()

    @property
    def main_image(self) -> str | None:
        image = self.images.filter(image_type=ProductImage.MAIN_IMAGE).first()
        if image:
            return image.image.url

    @property
    def preview(self) -> str | None:
        image = self.images.filter(image_type=ProductImage.PREVIEW).first()
        if image:
            return image.image.url

    @property
    def thumbnails(self) -> list | None:
        images = self.images.filter(image_type=ProductImage.THUMBNAIL).all()[:3]
        if images:
            return [item.image.url for item in images]
        return None

    def get_rating(self) -> int | None:
        rating = self.review.aggregate(rating=Avg("rating")).get("rating")
        if rating:
            rating = int(rating) if rating % 1 < 0.5 else int(rating + 1)
            return rating

    def get_total_quantity(self) -> int:
        total_quantity = self.items.aggregate(total_quantity=Sum("quantity")).get("total_quantity", 0)
        return total_quantity


class Seller(models.Model):
    title = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class ProductItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="items")
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.title} from {self.seller.title}"

    @property
    def price_with_discount(self) -> float | None:
        return DiscountManager(self).process()


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="review")
    rating = models.PositiveIntegerField(default=0)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review of {self.product.title} from {self.user.email}"


class ProductImage(models.Model):
    PREVIEW = "preview"
    MAIN_IMAGE = "main_image"
    THUMBNAIL = "thumbnail"
    IMAGE_TYPES = [
        (PREVIEW, "Preview image"),
        (MAIN_IMAGE, "Main product image"),
        (THUMBNAIL, "Shortened product images"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image_type = models.CharField(choices=IMAGE_TYPES)
    image = models.ImageField(upload_to=product_image_path)


class Discount(models.Model):
    PERCENT = "PERCENT"
    FIXED_AMOUNT = "FIXED_AMOUNT"
    FIXED_PRICE = "FIXED_PRICE"

    DISCOUNT_METHOD_CHOICES = [
        (PERCENT, "Percent"),
        (FIXED_AMOUNT, "Fixed amount"),
        (FIXED_PRICE, "Fixed price"),
    ]

    LEVEL_PRIORITY = [
        (0, "Low"),
        (1, "Medium"),
        (2, "High"),
    ]

    class Meta:
        abstract = True

    discount_method = models.CharField(max_length=15, choices=DISCOUNT_METHOD_CHOICES)
    value = models.PositiveIntegerField()
    priority = models.IntegerField(choices=LEVEL_PRIORITY)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()


class ProductDiscount(Discount):
    products = models.ManyToManyField(Product, related_name="discounts")


class CategoryDiscount(Discount):
    categories = models.ManyToManyField(Category, related_name="discounts")


class CartDiscount(Discount):
    min_items = models.PositiveIntegerField(null=True, blank=True)
    max_items = models.PositiveIntegerField(null=True, blank=True)
    min_total_price = models.PositiveIntegerField(null=True, blank=True)
    max_total_price = models.PositiveIntegerField(null=True, blank=True)
