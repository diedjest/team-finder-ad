from django import forms
from django.core.exceptions import ValidationError

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        if url and not url.startswith(("https://github.com/", "http://github.com/")):
            raise ValidationError(
                "Ссылка должна вести именно на Github (https://github.com/...)"
            )
        return url
