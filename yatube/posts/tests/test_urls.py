from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from posts.models import Group, Post


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_group',
        )
        cls.post = Post.objects.create(
            text='Test description of post',
            author=StaticURLTests.user,
        )
        cls.urls_template = (
            (
                '/',
                'posts/index.html'
            ),
            (
                f'/group/{StaticURLTests.group.slug}/',
                'posts/group_list.html'
            ),
            (
                f'/profile/{StaticURLTests.user.username}/',
                'posts/profile.html'
            ),
            (
                f'/posts/{StaticURLTests.post.id}/',
                'posts/post_detail.html'
            ),
            (
                '/create/',
                'posts/create_post.html'
            ),
            (
                f'/posts/{StaticURLTests.post.id}/edit/',
                'posts/create_post.html'
            ),
        )
        cls.urls_redirect = (
            ('/create/', '/auth/login/'),
            (f'/posts/{StaticURLTests.post.id}/edit/', '/auth/login/'),
            (f'/posts/{StaticURLTests.post.id}/comment/', '/auth/login/'),
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(StaticURLTests.user)
        cache.clear()

    def test_url_status_code(self):
        """Check status code for guest URLs."""
        for url, _ in StaticURLTests.urls_template:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_redirect_guest_user(self):
        """Check redirect for guest user for pages what need it."""
        for url, template in StaticURLTests.urls_redirect:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                template += '?next=' + url
                self.assertRedirects(response, template)

    def test_url_unexisting_page(self):
        """Unexisting page should have NOT_FOUND status code."""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_used_template(self):
        """Check correct template for pages."""
        for url, template in StaticURLTests.urls_template:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
