from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class Skill(models.Model):
    name = models.CharField(max_length=124, unique=True, verbose_name=_("Название"))

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
    
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(_("имя"), max_length=124)
    surname = models.CharField(_("фамилия"), max_length=124)
    
    avatar = models.ImageField(upload_to='avatars/', verbose_name=_("Аватар"))
    phone = models.CharField(max_length=12, verbose_name=_("Телефон"))
    github_url = models.URLField(max_length=200, null=True, blank=True, verbose_name=_("GitHub"))
    about = models.TextField(max_length=256, null=True, blank=True, verbose_name=_("О себе"))
    
    skills = models.ManyToManyField(Skill, related_name='users', blank=True, verbose_name=_("Навыки"))

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

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
