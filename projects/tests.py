from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Project
from .forms import ProjectForm

User = get_user_model()


class ProjectTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@test.com',
            password='password123',
            name='Иван',
            surname='Иванов',
            phone='+79991234567'
        )
        self.participant = User.objects.create_user(
            email='participant@test.com',
            password='password123',
            name='Петр',
            surname='Петров',
            phone='+79997654321'
        )

        self.project = Project.objects.create(
            name='Тестовый проект',
            description='Описание тестового проекта',
            owner=self.owner,
            status=Project.Status.OPEN
        )

    def test_project_str(self):
        """Проверка строкового отображения модели"""
        self.assertEqual(str(self.project), 'Тестовый проект')

    def test_project_form_valid(self):
        """Проверка формы с правильными данными"""
        form_data = {
            'name': 'Новый проект',
            'description': 'Текст',
            'github_url': 'https://github.com/user/repo',
            'status': 'open'
        }
        form = ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_project_form_invalid_github(self):
        """Проверка валидации поля github_url"""
        form_data = {
            'name': 'Новый проект',
            'github_url': 'https://google.com/',
            'status': 'open'
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('github_url', form.errors)

    def test_project_list_view(self):
        """Проверка доступности списка проектов для всех"""
        response = self.client.get(reverse('projects:project_list_alias'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Тестовый проект')

    def test_create_project_view(self):
        """Проверка создания проекта авторизованным пользователем"""
        self.client.login(email='owner@test.com', password='password123')
        response = self.client.post(reverse('projects:create_project'), {
            'name': 'Проект через POST',
            'description': 'Описание',
            'status': 'open'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Project.objects.filter(name='Проект через POST').exists()
        )

        new_project = Project.objects.get(name='Проект через POST')
        self.assertIn(self.owner, new_project.participants.all())

    def test_edit_project_forbidden(self):
        """Проверка, что чужой человек не может редактировать проект"""
        self.client.login(email='participant@test.com', password='password123')
        response = self.client.get(
            reverse('projects:edit_project', args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_toggle_participate_success(self):
        """Проверка успешного участия в проекте"""
        self.client.login(email='participant@test.com', password='password123')
        response = self.client.post(
            reverse('projects:toggle_participate', args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['participant'])
        self.assertIn(self.participant, self.project.participants.all())

    def test_toggle_participate_author_forbidden(self):
        """Проверка, что автор не может изменить свой статус участия"""
        self.client.login(email='owner@test.com', password='password123')
        response = self.client.post(
            reverse('projects:toggle_participate', args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 403)

    def test_toggle_participate_closed_project(self):
        """Проверка защиты: нельзя вступить в закрытый проект"""
        self.project.status = Project.Status.CLOSED
        self.project.save()

        self.client.login(email='participant@test.com', password='password123')
        response = self.client.post(
            reverse('projects:toggle_participate', args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['error'], 'Набор в проект завершен')

    def test_complete_project(self):
        """Проверка завершения проекта автором"""
        self.client.login(email='owner@test.com', password='password123')
        response = self.client.post(
            reverse('projects:complete_project', args=[self.project.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['project_status'], 'closed')

        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.Status.CLOSED)
