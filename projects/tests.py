from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import ProjectForm
from .models import Project

User = get_user_model()

OWNER_EMAIL = "owner@test.com"
PARTICIPANT_EMAIL = "participant@test.com"
TEST_PASSWORD = "password123"

OWNER_NAME = "Иван"
OWNER_SURNAME = "Иванов"
OWNER_PHONE = "+79991234567"

PARTICIPANT_NAME = "Петр"
PARTICIPANT_SURNAME = "Петров"
PARTICIPANT_PHONE = "+79997654321"

TEST_PROJECT_NAME = "Тестовый проект"
TEST_PROJECT_DESC = "Описание тестового проекта"

NEW_PROJECT_NAME = "Новый проект"
POST_PROJECT_NAME = "Проект через POST"

VALID_GITHUB_URL = "https://github.com/user/repo"
INVALID_GITHUB_URL = "https://google.com/"

CLOSED_ERROR_MSG = "Набор в проект завершен"


class ProjectTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email=OWNER_EMAIL,
            password=TEST_PASSWORD,
            name=OWNER_NAME,
            surname=OWNER_SURNAME,
            phone=OWNER_PHONE,
        )
        self.participant = User.objects.create_user(
            email=PARTICIPANT_EMAIL,
            password=TEST_PASSWORD,
            name=PARTICIPANT_NAME,
            surname=PARTICIPANT_SURNAME,
            phone=PARTICIPANT_PHONE,
        )

        self.project = Project.objects.create(
            name=TEST_PROJECT_NAME,
            description=TEST_PROJECT_DESC,
            owner=self.owner,
            status=Project.Status.OPEN,
        )

    def test_project_str(self):
        """Проверка строкового отображения модели"""
        self.assertEqual(str(self.project), TEST_PROJECT_NAME)

    def test_project_form_valid(self):
        """Проверка формы с правильными данными"""
        form_data = {
            "name": NEW_PROJECT_NAME,
            "description": "Текст",
            "github_url": VALID_GITHUB_URL,
            "status": Project.Status.OPEN.value,
        }
        form = ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_project_form_invalid_github(self):
        """Проверка валидации поля github_url"""
        form_data = {
            "name": NEW_PROJECT_NAME,
            "github_url": INVALID_GITHUB_URL,
            "status": Project.Status.OPEN.value,
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("github_url", form.errors)

    def test_project_list_view(self):
        """Проверка доступности списка проектов для всех"""
        response = self.client.get(reverse("projects:project_list_alias"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, TEST_PROJECT_NAME)

    def test_create_project_view(self):
        """Проверка создания проекта авторизованным пользователем"""
        self.client.login(email=OWNER_EMAIL, password=TEST_PASSWORD)
        response = self.client.post(
            reverse("projects:create_project"),
            {
                "name": POST_PROJECT_NAME,
                "description": "Описание",
                "status": Project.Status.OPEN.value,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(name=POST_PROJECT_NAME).exists())

        new_project = Project.objects.get(name=POST_PROJECT_NAME)
        self.assertIn(self.owner, new_project.participants.all())

    def test_edit_project_forbidden(self):
        """Проверка, что чужой человек не может редактировать проект"""
        self.client.login(email=PARTICIPANT_EMAIL, password=TEST_PASSWORD)
        response = self.client.get(
            reverse("projects:edit_project", args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_toggle_participate_success(self):
        """Проверка успешного участия в проекте"""
        self.client.login(email=PARTICIPANT_EMAIL, password=TEST_PASSWORD)
        response = self.client.post(
            reverse("projects:toggle_participate", args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["participant"])
        self.assertIn(self.participant, self.project.participants.all())

    def test_toggle_participate_author_forbidden(self):
        """Проверка, что автор не может изменить свой статус участия"""
        self.client.login(email=OWNER_EMAIL, password=TEST_PASSWORD)
        response = self.client.post(
            reverse("projects:toggle_participate", args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_toggle_participate_closed_project(self):
        """Проверка защиты: нельзя вступить в закрытый проект"""
        self.project.status = Project.Status.CLOSED
        self.project.save()

        self.client.login(email=PARTICIPANT_EMAIL, password=TEST_PASSWORD)
        response = self.client.post(
            reverse("projects:toggle_participate", args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], CLOSED_ERROR_MSG)

    def test_complete_project(self):
        """Проверка завершения проекта автором"""
        self.client.login(email=OWNER_EMAIL, password=TEST_PASSWORD)
        response = self.client.post(
            reverse("projects:complete_project", args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["project_status"], Project.Status.CLOSED.value)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.Status.CLOSED)
