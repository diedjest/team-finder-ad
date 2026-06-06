import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Skill
from .forms import UserProfileEditForm

User = get_user_model()


class UsersTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='password123',
            name='Иван',
            surname='Иванов',
            phone='+79991234567'
        )
        self.skill = Skill.objects.create(name='Python')

    def test_create_user(self):
        """Проверка успешного создания пользователя с нужными полями"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('password123'))

    def test_skill_str(self):
        """Проверка строкового отображения навыка"""
        self.assertEqual(str(self.skill), 'Python')

    def test_valid_phone_number_conversion(self):
        """Проверка, что номер, начинающийся с 8, конвертируется в +7"""
        form_data = {
            'name': 'Петр', 'surname': 'Петров',
            'phone': '89991112233',
            'github_url': 'https://github.com/test'
        }
        form = UserProfileEditForm(data=form_data, instance=self.user)

        self.assertTrue(form.is_valid(), msg=f"Ошибки формы: {form.errors}")
        self.assertEqual(form.cleaned_data['phone'], '+79991112233')

    def test_invalid_phone_number(self):
        """Проверка, что короткий или неправильный номер не пройдет"""
        form_data = {
            'name': 'Петр', 'surname': 'Петров',
            'phone': '12345'
        }
        form = UserProfileEditForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_duplicate_phone_number(self):
        """Проверка уникальности номера телефона"""
        form_data = {
            'name': 'Петр', 'surname': 'Петров',
            'phone': '+79991234567'
        }
        form = UserProfileEditForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_invalid_github_url(self):
        """Проверка, что ссылка ведет именно на GitHub"""
        form_data = {
            'name': 'Петр', 'surname': 'Петров',
            'phone': '+79991112233',
            'github_url': 'https://vk.com/test'
        }
        form = UserProfileEditForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('github_url', form.errors)

    def test_add_existing_skill_api(self):
        """Проверка добавления существующего навыка через API"""
        self.client.login(email='test@example.com', password='password123')
        url = reverse('users:add_skill', args=[self.user.pk])

        response = self.client.post(
            url,
            data=json.dumps({'skill_id': self.skill.id}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.skill, self.user.skills.all())
        self.assertEqual(response.json()['skill_id'], self.skill.id)

    def test_add_new_skill_api(self):
        """Проверка создания совершенно нового навыка через API"""
        self.client.login(email='test@example.com', password='password123')
        url = reverse('users:add_skill', args=[self.user.pk])

        response = self.client.post(
            url,
            data=json.dumps({'name': 'Django'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Skill.objects.filter(name='Django').exists())
        self.assertEqual(response.json()['created'], True)

    def test_remove_skill_api(self):
        """Проверка удаления навыка из профиля"""
        self.user.skills.add(self.skill)
        self.client.login(email='test@example.com', password='password123')

        url = reverse('users:remove_skill', args=[self.user.pk, self.skill.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.skill, self.user.skills.all())
