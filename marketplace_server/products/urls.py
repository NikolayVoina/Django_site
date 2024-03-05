from django.urls import path

from products.views import ComparisonView, ProductDetailView, ProductListView, add_to_comparison, remove_from_comparison

app_name = "products"

urlpatterns = [
    path("", ProductListView.as_view(), name="catalog"),
    path("<int:pk>/", ProductDetailView.as_view(), name="product"),
    path("comparison/", ComparisonView.as_view(), name="comparison"),
    path("comparison/add/<int:product_id>/", add_to_comparison, name="add_to_comparison"),
    path("comparison/remove/<int:product_id>/", remove_from_comparison, name="remove_from_comparison"),
]
