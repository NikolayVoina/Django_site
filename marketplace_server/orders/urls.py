from django.urls import path

from orders.views import CartTemplateView, OrderCreateView, OrderDetailView, cart_add, cart_remove

app_name = "orders"

urlpatterns = [
    path("cart/add/<int:product_item_id>/", cart_add, name="cart_add"),
    path("cart/remove/<int:product_item_id>/", cart_remove, name="cart_remove"),
    path("cart/", CartTemplateView.as_view(), name="cart"),
    path("checkout/", OrderCreateView.as_view(), name="checkout"),
    path("<int:pk>/", OrderDetailView.as_view(), name="detail"),
]
