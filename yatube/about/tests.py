from http import HTTPStatus

from django.test import Client, TestCase


class UrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_url_status_code(self):
        urls = [
            '/about/author/',
            '/about/tech/',
            '/about/none/',
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_template(self):
        templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
            '/about/none/': 'about/none.html',
        }
        for address, template in templates.items():
            with self.subTest(address=address):
                result = self.guest_client.get(address)
                self.assertTemplateUsed(result, template)
