import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import UserProfileEditForm
from .models import Skill

User = get_user_model()

TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password123"
TEST_NAME = "Иван"
TEST_SURNAME = "Иванов"
TEST_PHONE = "+79991234567"

TEST_SKILL_NAME = "Python"
NEW_SKILL_NAME = "Django"

FORM_NAME = "Петр"
FORM_SURNAME = "Петров"
RAW_PHONE = "89991112233"
FORMATTED_PHONE = "+79991112233"
INVALID_PHONE = "12345"

VALID_GITHUB_URL = "https://github.com/test"
INVALID_GITHUB_URL = "https://vk.com/test"

CONTENT_TYPE_JSON = "application/json"


class UsersTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            name=TEST_NAME,
            surname=TEST_SURNAME,
            phone=TEST_PHONE,
        )
        self.skill = Skill.objects.create(name=TEST_SKILL_NAME)

    def test_create_user(self):
        self.assertEqual(self.user.email, TEST_EMAIL)
        self.assertTrue(self.user.check_password(TEST_PASSWORD))

    def test_skill_str(self):
        self.assertEqual(str(self.skill), TEST_SKILL_NAME)

    def test_valid_phone_number_conversion(self):
        form_data = {
            "name": FORM_NAME,
            "surname": FORM_SURNAME,
            "phone": RAW_PHONE,
            "github_url": VALID_GITHUB_URL,
        }
        form = UserProfileEditForm(data=form_data, instance=self.user)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["phone"], FORMATTED_PHONE)

    def test_invalid_phone_number(self):
        form_data = {"name": FORM_NAME, "surname": FORM_SURNAME, "phone": INVALID_PHONE}
        form = UserProfileEditForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_duplicate_phone_number(self):
        form_data = {"name": FORM_NAME, "surname": FORM_SURNAME, "phone": TEST_PHONE}
        form = UserProfileEditForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)

    def test_invalid_github_url(self):
        form_data = {
            "name": FORM_NAME,
            "surname": FORM_SURNAME,
            "phone": FORMATTED_PHONE,
            "github_url": INVALID_GITHUB_URL,
        }
        form = UserProfileEditForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("github_url", form.errors)

    def test_add_existing_skill_api(self):
        self.client.login(email=TEST_EMAIL, password=TEST_PASSWORD)
        url = reverse("users:add_skill", args=[self.user.pk])

        response = self.client.post(
            url,
            data=json.dumps({"skill_id": self.skill.id}),
            content_type=CONTENT_TYPE_JSON,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.skill, self.user.skills.all())
        self.assertEqual(response.json()["skill_id"], self.skill.id)

    def test_add_new_skill_api(self):
        self.client.login(email=TEST_EMAIL, password=TEST_PASSWORD)
        url = reverse("users:add_skill", args=[self.user.pk])

        response = self.client.post(
            url,
            data=json.dumps({"name": NEW_SKILL_NAME}),
            content_type=CONTENT_TYPE_JSON,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Skill.objects.filter(name=NEW_SKILL_NAME).exists())
        self.assertEqual(response.json()["created"], True)

    def test_remove_skill_api(self):
        self.user.skills.add(self.skill)
        self.client.login(email=TEST_EMAIL, password=TEST_PASSWORD)

        url = reverse("users:remove_skill", args=[self.user.pk, self.skill.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.skill, self.user.skills.all())
