from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError

from .utils import normalize_and_validate_phone

User = get_user_model()


def validate_github_url(url):
    if url and not url.startswith(("https://github.com/", "http://github.com/")):
        raise ValidationError(
            "Ссылка должна вести именно на Github (https://github.com/...)."
        )


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label="Email address", widget=forms.EmailInput(attrs={"autofocus": True})
    )
    password = forms.CharField(
        label="Пароль", strip=False, widget=forms.PasswordInput()
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user_cache = authenticate(self.request, email=email, password=password)

            if self.user_cache is None:
                raise ValidationError("Неверный email или пароль")

        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        widgets = {
            "about": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        exclude_pk = self.instance.pk if self.instance else None
        return normalize_and_validate_phone(phone, exclude_pk)

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        validate_github_url(url)
        return url
