from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


def get_count_users():
    return User.objects.count()


class TestUserForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.form_content = {
            'first_name': 'Testfirstname',
            'last_name': 'TestLastname',
            'username': 'test_user',
            'email': 'test@mail.ru',
            'password1': 'ljasdufilq2312',
            'password2': 'ljasdufilq2312',
        }

    def test_create_user(self):
        users_count = get_count_users()
        response = self.guest_client.post(
            reverse('users:signup'),
            data=TestUserForm.form_content,
            follow=True,
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(get_count_users(), users_count + 1)
        self.assertTrue(User.objects.filter(
            first_name=TestUserForm.form_content.get('first_name'),
            last_name=TestUserForm.form_content.get('last_name'),
            username=TestUserForm.form_content.get('username'),
            email=TestUserForm.form_content.get('email'),
        ))
