from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.shortcuts import reverse


class UrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.user = User.objects.create_user(username='test_user')
        # urls - ( (url, template, redirect) )
        cls.urls = (
            (
                reverse('users:signup'),
                '',
                '',
            ),
            (
                reverse('users:login'),
                'users/login.html',
                '',
            ),
            (
                reverse('users:password_change'),
                'users/password_change.html',
                '/auth/login/',
            ),
            (
                reverse('users:password_change_done'),
                'users/password_change_done.html',
                '/auth/login/',
            ),
            (
                reverse('users:password_reset'),
                'users/password_reset_form.html',
                '',
            ),
            (
                reverse('users:password_reset_done'),
                'users/password_reset_done.html',
                '',
            ),
            (
                reverse('users:password_reset_confirm', args=['uid', 'token']),
                'users/password_reset_confirm.html',
                '',
            ),
            (
                reverse('users:password_reset_complete'),
                'users/password_reset_complete.html',
                '',
            ),
            (
                reverse('users:logout'),
                'users/logged_out.html',
                '',
            ),
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_status_code(self):
        """Check status code for all urls."""
        for url, _, _ in UrlTests.urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_guest_user_redirect(self):
        """Check redirect on URLs."""
        for url, _, redirect in UrlTests.urls:
            if redirect != '':
                with self.subTest(url=url):
                    response = self.guest_client.get(url)
                    redirect = redirect + '?next=' + url
                    self.assertRedirects(response, redirect)

    def test_url_template_used(self):
        """Check used templates of URLs."""
        for url, template, _ in UrlTests.urls:
            if template != '':
                with self.subTest(url=url):
                    response = self.authorized_client.get(url)
                    self.assertTemplateUsed(response, template)
