from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from users.forms import CreationForm

User = get_user_model()


class TestView(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.guest_user = Client()

    def test_form_creating_user(self):
        response = self.guest_user.get(reverse('users:signup'))
        self.assertTemplateUsed(response, 'users/signup.html')
        self.assertIsInstance(response.context.get('form'), CreationForm)
