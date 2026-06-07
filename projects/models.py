from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

NAME_MAX_LENGTH = 200
GITHUB_URL_MAX_LENGTH = 200
STATUS_MAX_LENGTH = 6


class Project(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", _("Open")
        CLOSED = "closed", _("Closed")

    name = models.CharField(
        max_length=NAME_MAX_LENGTH, verbose_name=_("Название проекта")
    )
    description = models.TextField(blank=True, verbose_name=_("Описание проекта"))
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name=_("Автор"),
    )
    github_url = models.URLField(
        max_length=GITHUB_URL_MAX_LENGTH,
        null=True,
        blank=True,
        verbose_name=_("GitHub репозиторий"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Дата публикации")
    )
    status = models.CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name=_("Статус"),
    )

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name=_("Участники"),
    )

    class Meta:
        verbose_name = _("Проект")
        verbose_name_plural = _("Проекты")
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
