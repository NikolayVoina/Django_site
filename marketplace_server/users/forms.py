from allauth.account.forms import LoginForm, ResetPasswordForm, ResetPasswordKeyForm, SignupForm
from django import forms
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

from users.models import User

NAME_ATTRS = {
    "class": "form-control",
    "id": "inputName",
    "type": "text",
    "placeholder": "Имя",
    "aria-describedby": "validationServerName"
}

EMAIL_ATTRS = {
    "class": "form-control",
    "id": "inputEmail",
    "type": "email",
    "placeholder": "Адрес электронной почты",
    "aria-describedby": "validationServerEmail",
}

PASSWORD_ATTRS = {
    "class": "form-control",
    "id": "inputPassword",
    "type": "password",
    "placeholder": "Пароль",
    "aria-describedby": "validationServerPassword",
}


def fields_validate(form: forms.Form, fields_to_check: list) -> None:
    for field in fields_to_check:
        if field in form.errors.keys():
            form.fields[field].widget.attrs["class"] = "form-control is-invalid"


class MarketplaceSignupForm(SignupForm):
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs=NAME_ATTRS))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(EMAIL_ATTRS)
        self.fields["password1"].widget.attrs.update(PASSWORD_ATTRS)

    def clean_first_name(self) -> list:
        names = self.cleaned_data["first_name"].split()
        if len(names) > 2:
            self.add_error("first_name", "Введите в формате: Имя Фамилия.")
            self.fields["first_name"].widget.attrs["class"] = "form-control is-invalid"
        if len(names) == 2:
            self.cleaned_data["last_name"] = names[1]
        return names

    def clean(self) -> dict:
        clean = super().clean()
        fields_validate(self, ["email", "password1"])
        return clean

    def save(self, request: str) -> User:
        user = super().save(request)

        names = self.cleaned_data["first_name"]
        if len(names) == 2:
            user.first_name = names[0]
            user.last_name = names[1]
        elif names:
            user.first_name = names[0]
        user.save()
        return user


class MarketplaceLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["login"].widget.attrs.update(EMAIL_ATTRS)
        self.fields["password"].widget.attrs.update(PASSWORD_ATTRS)

        forgot_password_txt = "Забыли пароль?"
        self.fields["password"].help_text = mark_safe(
            f'<a href=\"{reverse_lazy("users:forgot_password")}\" '
            f'class="small link-dark" '
            f'style="text-decoration: None;">{forgot_password_txt}</a>'
        )


class MarketplaceProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["avatar", "first_name", "last_name", "city", "address", "phone_number"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["avatar"].widget = forms.FileInput()
        self.fields["avatar"].widget.attrs.update(
            {
                "class": "form-control",
                "id": "userImage",
                "aria-describedby": "validationServerAvatar",
                "accept": "image/*"
            }
        )
        self.fields["first_name"].widget.attrs.update(
            {
                "class": "form-control",
                "aria-label": "First name",
                "value": self.instance.first_name
            }
        )
        self.fields["last_name"].widget.attrs.update(
            {
                "class": "form-control",
                "aria-label": "Last name",
                "value": self.instance.last_name
            }
        )
        self.fields["city"].widget.attrs.update(
            {
                "class": "form-control",
                "aria-label": "City",
                "placeholder": "Москва",
                "value": "" if self.instance.city is None else self.instance.city
            }
        )
        self.fields["address"].widget = forms.TextInput()
        self.fields["address"].widget.attrs.update(
            {
                "class": "form-control",
                "aria-label": "Address",
                "placeholder": "ул. Мира, дом 25, подъезд 1, кв. 13, 600138",
                "value": "" if self.instance.address is None else self.instance.address,
            }
        )
        self.fields["phone_number"].widget.attrs.update(
            {
                "class": "form-control",
                "aria-label": "userPhone",
                "aria-describedby": "validationServerPhone",
                "placeholder": "+ 7 (918) 123 50 18",
                "value": "" if self.instance.phone_number is None else self.instance.phone_number,
            }
        )

    def clean(self) -> dict:
        clean = super().clean()
        fields_validate(self, ["avatar", "first_name", "last_name", "city", "address"])
        return clean

    def clean_phone_number(self) -> str:
        phone_number = self.cleaned_data["phone_number"]
        if phone_number is None:
            return ""
        if phone_number[:2] != "+7" or len(phone_number) != 12:
            self.add_error(
                "phone_number",
                "Номер телефона должен начинаться с +7 и не содержать более 12 символов."
            )
            self.fields["phone_number"].widget.attrs["class"] = "form-control is-invalid"
        return phone_number


class MarketplaceResetPasswordForm(ResetPasswordForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update(EMAIL_ATTRS)

    def clean(self) -> dict:
        clean = super().clean()
        fields_validate(self, ["email"])
        return clean


class MarketplaceResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update(PASSWORD_ATTRS)
        self.fields["password2"].widget.attrs.update(PASSWORD_ATTRS)

    def clean(self) -> dict:
        clean = super().clean()
        fields_validate(self, ["password1", "password2"])
        return clean
