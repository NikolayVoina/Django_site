from django import forms

from orders.models import Order


class OrderCreateForm(forms.ModelForm):
    first_name = forms.CharField(required=True, widget=forms.TextInput())
    last_name = forms.CharField(required=True, widget=forms.TextInput())
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "placeholder": "example@mail.com", "required": True
    }))
    phone_number = forms.CharField(widget=forms.TextInput(attrs={
        "placeholder": "+7 (918) 080 94 51"
    }))
    city = forms.CharField(widget=forms.TextInput(attrs={
        "placeholder": "Москва"
    }))
    address = forms.CharField(widget=forms.TextInput(attrs={
        "placeholder": "ул. Мира, дом 25, подъезд 1, кв. 13"
    }))
    post_code = forms.CharField(widget=forms.TextInput(attrs={
        "placeholder": "600138"
    }))
    payment_method = forms.ChoiceField(choices=Order.PAYMENT_METHODS, widget=forms.RadioSelect())
    same_address = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        "id": "same-address"
    }))
    save_info = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={
        "id": "save-info"
    }))

    class Meta:
        model = Order
        fields = ("payment_method",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field in ("first_name", "last_name", "email", "phone_number", "city", "address", "post_code"):
                self.fields.get(field).widget.attrs["class"] = "form-control"
            if field in ("payment_method", "same_address", "save_info"):
                self.fields.get(field).widget.attrs["class"] = "form-check-input"
