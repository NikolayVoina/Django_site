from django import forms
from django.db.models import QuerySet, Sum

from .models import Review


class ProductFilterForm(forms.Form):
    title = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Название"})
    )
    min_price = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "от 1 000"})
    )
    max_price = forms.DecimalField(
        required=False, min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "от 3 000"})
    )
    in_stock = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        title = self.cleaned_data.get("title")
        min_price = self.cleaned_data.get("min_price")
        max_price = self.cleaned_data.get("max_price")
        in_stock = self.cleaned_data.get("in_stock")

        if title:
            queryset = queryset.filter(title__icontains=title)

        if min_price:
            queryset = queryset.filter(items__price__gte=min_price)

        if max_price:
            queryset = queryset.filter(items__price__lte=max_price)

        if in_stock:
            queryset = queryset.annotate(total_quantity=Sum("items__quantity")).filter(total_quantity__gt=0)

        return queryset


class ReviewForm(forms.ModelForm):
    comment = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control", "rows": "3"}))

    class Meta:
        model = Review
        fields = ["user", "product", "rating", "comment"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
