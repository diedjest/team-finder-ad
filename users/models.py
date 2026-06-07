from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager

SKILL_NAME_MAX_LENGTH = 124
USER_NAME_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 12
GITHUB_URL_MAX_LENGTH = 200
ABOUT_MAX_LENGTH = 256


class Skill(models.Model):
    name = models.CharField(
        max_length=SKILL_NAME_MAX_LENGTH, unique=True, verbose_name=_("Название")
    )

    class Meta:
        verbose_name = _("Навык")
        verbose_name_plural = _("Навыки")
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None

    email = models.EmailField(_("email address"), unique=True)
    name = models.CharField(_("имя"), max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField(_("фамилия"), max_length=USER_NAME_MAX_LENGTH)

    avatar = models.ImageField(upload_to="avatars/", verbose_name=_("Аватар"))
    phone = models.CharField(max_length=PHONE_MAX_LENGTH, verbose_name=_("Телефон"))
    github_url = models.URLField(
        max_length=GITHUB_URL_MAX_LENGTH,
        null=True,
        blank=True,
        verbose_name=_("GitHub"),
    )
    about = models.TextField(
        max_length=ABOUT_MAX_LENGTH, null=True, blank=True, verbose_name=_("О себе")
    )

    skills = models.ManyToManyField(
        Skill, related_name="users", blank=True, verbose_name=_("Навыки")
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.avatar:
            from .utils import generate_avatar

            avatar_file = generate_avatar(self.name)
            self.avatar.save(avatar_file.name, avatar_file, save=False)
        super().save(*args, **kwargs)

    @property
    def owned_projects(self):
        return self.created_projects.all()

    @property
    def participated_projects(self):
        return self.projects_participated.all()

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return f"{self.name} {self.surname}"
