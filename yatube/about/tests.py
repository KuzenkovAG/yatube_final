from http import HTTPStatus

from django.test import Client, TestCase


class UrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.urls = (
            ('/about/author/', 'about/author.html'),
            ('/about/tech/', 'about/tech.html'),
            ('/about/none/', 'about/none.html'),
        )

    def test_url_status_code(self):
        for url, _ in UrlTest.urls:
            with self.subTest(url=url):
                response = UrlTest.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_template(self):
        for url, template in UrlTest.urls:
            with self.subTest(url=url):
                result = UrlTest.guest_client.get(url)
                self.assertTemplateUsed(result, template)
