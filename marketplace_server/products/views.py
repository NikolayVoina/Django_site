from itertools import chain

from django.db.models import Avg, Min, QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, reverse
from django.views.generic import DetailView, ListView, TemplateView

from products.forms import ProductFilterForm, ReviewForm
from products.models import Category, Product
from products.utils import Comparison, same_page_url


class ProductListView(ListView):
    model = Product
    template_name = "catalog.html"
    context_object_name = "products"
    paginate_by = 6

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        sort = self.request.GET.get("sort")
        category_id = self.request.GET.get("category")
        form = ProductFilterForm(self.request.GET)

        if category_id:
            category = Category.objects.get(id=category_id)
            subcategory_ids = set(category.category_set.values_list("id", flat=True))
            if subcategory_ids:
                subcategory_ids.add(int(category_id))
                queryset = queryset.filter(category_id__in=subcategory_ids)
            else:
                queryset = queryset.filter(category_id=category_id)

        if form.is_valid():
            queryset = form.filter_queryset(queryset)

        if sort == "price":
            self.request.session["price_sort"] = "desc" if self.request.session.get("price_sort") == "asc" else "asc"
            order = "-" if self.request.session["price_sort"] == "desc" else ""
            queryset = queryset.annotate(lowest_item_price=Min("items__price")).order_by(f"{order}lowest_item_price")

        if sort == "review":
            self.request.session["review_sort"] = "desc" if self.request.session.get("review_sort") == "asc" else "asc"
            order = "-" if self.request.session["review_sort"] == "desc" else ""
            products_with_rating = queryset.exclude(review=None).annotate(
                review__rating=Avg("review__rating")).order_by(f"{order}review__rating")
            products_without_rating = queryset.filter(review=None)
            queryset = list(chain(products_with_rating, products_without_rating))

        if sort == "date":
            self.request.session["date_sort"] = "desc" if self.request.session.get("date_sort") == "asc" else "asc"
            order = "-" if self.request.session["date_sort"] == "desc" else ""
            queryset = queryset.order_by(f"{order}created_at")

        return queryset

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["filter_form"] = ProductFilterForm(self.request.GET)
        context["categories"] = Category.objects.all()
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "product.html"
    context_object_name = "product"

    def get(self, request: HttpRequest, *args, **kwargs):  # noqa: ANN201
        self.request.user.add_view_history(self.get_object())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context["reviews"] = self.object.review.order_by("-updated_at")
        context["review_form"] = ReviewForm()
        return context

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponseRedirect:
        product = self.get_object()
        data = {
            "user": request.user,
            "product": product,
            "rating": 1,
            "comment": request.POST.get("comment"),
        }
        form = ReviewForm(data)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect(reverse("products:product", kwargs={"pk": product.pk}))


def add_to_comparison(request: HttpRequest, product_id: int) -> HttpResponse:
    comparison = Comparison(request)
    comparing_product = get_object_or_404(Product, pk=product_id)
    comparison.add(comparing_product)
    redirect_url = same_page_url(request, reverse("index"))
    return redirect(redirect_url)


def remove_from_comparison(request: HttpRequest, product_id: int) -> HttpResponse:
    comparison = Comparison(request)
    product_item = get_object_or_404(Product, pk=product_id)
    comparison.remove(product_item)
    redirect_url = same_page_url(request, reverse("products:comparison"))
    return redirect(redirect_url)


class ComparisonView(TemplateView):
    template_name = "comparison.html"
