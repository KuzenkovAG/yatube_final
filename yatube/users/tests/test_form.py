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

    def test_create_user(self):
        users_count = get_count_users()
        form_content = {
            'username': 'test_user',
            'password1': 'ljasdufilq2312',
            'password2': 'ljasdufilq2312',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_content,
            follow=True,
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(get_count_users(), users_count + 1)
        self.assertTrue(User.objects.filter(
            username=form_content.get('username'),
        ))
