from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, TemplateView

from orders.cart import Cart
from orders.forms import OrderCreateForm
from orders.models import Order
from products.models import ProductItem
from products.utils import same_page_url


def cart_add(request: HttpRequest, product_item_id: ProductItem.pk) -> HttpResponse:
    cart = Cart(request)
    product_item = get_object_or_404(ProductItem, pk=product_item_id)
    cart.add(product_item)
    redirect_url = same_page_url(request, reverse("products:catalog"))
    return redirect(redirect_url)


def cart_remove(request: HttpRequest, product_item_id: ProductItem.pk) -> HttpResponse:
    cart = Cart(request)
    product_item = get_object_or_404(ProductItem, pk=product_item_id)
    cart.remove(product_item)
    redirect_url = same_page_url(request, reverse("products:catalog"))
    return redirect(redirect_url)


class CartTemplateView(TemplateView):
    template_name = "cart.html"


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderCreateForm
    template_name = "checkout.html"
    login_url = reverse_lazy("users:login")

    def get_initial(self) -> dict:
        initial = super().get_initial()
        initial.update(
            {
                "first_name": self.request.user.first_name,
                "last_name": self.request.user.last_name,
                "email": self.request.user.email,
                "phone_number": self.request.user.phone_number,
                "city": self.request.user.city,
                "address": self.request.user.address,
                "payment_method": Order.BY_CARD
            }
        )
        return initial

    def form_valid(self, form: OrderCreateForm) -> HttpResponseRedirect:
        self.object = form.save(commit=False)
        delivery_info = {
            "first_name": form.cleaned_data.get("first_name"),
            "last_name": form.cleaned_data.get("last_name"),
            "email": form.cleaned_data.get("email"),
            "city": form.cleaned_data.get("city"),
            "address": form.cleaned_data.get("address"),
            "phone_number": form.cleaned_data.get("phone_number"),
            "post_code": form.cleaned_data.get("post_code"),
        }
        self.object.user = self.request.user
        self.object.delivery_info = delivery_info
        self.object.save()

        if form.cleaned_data.get("save_info"):
            self.request.user.update_delivery_info(**delivery_info)

        cart = Cart(self.request)
        cart.copy_to_order(self.object)

        message_txt = str(
            f"Заказ №{self.object.id} успешно создан. "
            f"Следите за статусом заказа здесь или в личном кабинете."
        )
        messages.info(self.request, message_txt, extra_tags="checkout")
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse("orders:detail", kwargs={"pk": self.object.pk})


class OrderDetailView(DetailView):
    template_name = "order.html"
    model = Order
    context_object_name = "order"
