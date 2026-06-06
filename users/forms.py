import re
from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError

User = get_user_model()


def validate_github_url(url):
    if url and not url.startswith(
        ('https://github.com/', 'http://github.com/')
    ):
        raise ValidationError(
            "Ссылка должна вести именно на Github (https://github.com/...)."
        )


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput()
    )

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
        label="Email address",
        widget=forms.EmailInput(attrs={'autofocus': True})
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput()
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(
                self.request,
                email=email,
                password=password
            )

            if self.user_cache is None:
                raise ValidationError("Неверный email или пароль")

        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('name', 'surname', 'avatar', 'about', 'phone', 'github_url')
        widgets = {
            'about': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise ValidationError("Это поле обязательно.")

        if not re.match(r'^(8|\+7)\d{10}$', phone):
            raise ValidationError(
                "Номер телефона должен быть"
                " в формате 8XXXXXXXXXX или +7XXXXXXXXXX."
                )

        if phone.startswith('8'):
            phone = '+7' + phone[1:]

        qs = User.objects.filter(phone=phone)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError(
                "Пользователь с таким номером телефона уже существует."
            )

        return phone

    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        validate_github_url(url)
        return url
