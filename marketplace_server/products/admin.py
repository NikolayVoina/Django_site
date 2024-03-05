from django import forms
from django.contrib import admin

from products.models import (
    CartDiscount,
    Category,
    CategoryDiscount,
    Product,
    ProductDiscount,
    ProductImage,
    ProductItem,
    Review,
    Seller,
)


class ProductItemTabularInline(admin.TabularInline):
    model = ProductItem
    fields = ("id", "seller", "price", "quantity", "created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")
    extra = 0


class ReviewTabularInline(admin.TabularInline):
    model = Review
    fields = ("id", "user", "rating", "comment", "created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")
    extra = 0


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fields = ("id", "image_type", "image")
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_limited_edition", "is_daily_special")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("title",)
    fieldsets = [
        (
            None, {
                "fields": ("id", "title", "description"),
            }
        ),
        (
            "Detailed product information", {
                "fields": ("category", "characteristics", "is_limited_edition", "is_daily_special",
                           ("created_at", "updated_at")),
            }
        ),
    ]
    inlines = (ProductItemTabularInline, ReviewTabularInline, ProductImageInline)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "parent", "description", "is_preferred")
    readonly_fields = ("id",)
    ordering = ("title",)
    fieldsets = [
        (
            None, {
                "fields": ("id", "title"),
            }),
        (
            "Parent category", {
                "fields": ("parent",),
                "classes": ("collapse",),
            }
        ),
        (
            "Description category", {
                "fields": ("description",),
            }
        ),
        (
            "Preferred category", {
                "fields": ("is_preferred",),
            }
        ),
    ]

    def preferred_category(self) -> bool:
        if self.cleaned_data["is_preferred"] > 3:
            raise forms.ValidationError("Может быть создано не более 3 категорий с флагом is_preferred=True")

        return self.cleaned_data["is_preferred"]


@admin.register(Seller)
class Seller(admin.ModelAdmin):
    list_display = ("title",)


@admin.register(CartDiscount)
class CartDiscountAdmin(admin.ModelAdmin):
    list_display = ("pk", "discount_method", "priority", "valid_from", "valid_to")
    list_display_links = ("pk", "discount_method")


@admin.register(CategoryDiscount)
class CategoryDiscountAdmin(admin.ModelAdmin):
    list_display = ("pk", "discount_method", "priority", "valid_from", "valid_to")
    list_display_links = ("pk", "discount_method")


@admin.register(ProductDiscount)
class ProductDiscountAdmin(admin.ModelAdmin):
    list_display = ("pk", "discount_method", "priority", "valid_from", "valid_to")
    list_display_links = ("pk", "discount_method")
