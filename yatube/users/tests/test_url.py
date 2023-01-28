from django.contrib.auth import get_user_model
from django.test import Client, TestCase


class UrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.user = User.objects.create_user(username='test_user')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_status_code(self):
        urls = {
            '/auth/signup/': 'OK',
            '/auth/login/': 'OK',
            '/auth/password_change/': 'OK',
            '/auth/password_change_done/': 'OK',
            '/auth/password_reset/': 'OK',
            '/auth/password_reset/done/': 'OK',
            '/auth/reset/uidb64/token/': 'OK',
            '/auth/reset/done/': 'OK',
            '/auth/logout/': 'OK',
        }
        for address in urls.keys():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_url_guest_user_redirect(self):
        redirects = {
            '/auth/password_change/': '/auth/login/',
            '/auth/password_change_done/': '/auth/login/',
        }
        for address, redirect in redirects.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                redirect = redirect + '?next=' + address
                self.assertRedirects(response, redirect)

    def test_url_template_used(self):
        templates = {
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change.html',
            '/auth/password_change_done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/uidb64/token/': 'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        for address, template in templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
