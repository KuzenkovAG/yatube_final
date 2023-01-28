from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.user = User.objects.create(username='auth_test')
        cls.group_title = 'test_title'
        cls.group = Group.objects.create(
            title=cls.group_title,
            slug='test_slug',
            description='test_description',
        )
        cls.post_text_short = 'test_text'
        cls.post = Post.objects.create(
            text=cls.post_text_short,
            author=cls.user,
        )
        cls.post_text_long = ('Очень длинная строка, которая превышает '
                              'ограничение')
        cls.post_long = Post.objects.create(
            text=cls.post_text_long,
            author=cls.user,
        )

    def test_str_short_string(self):
        self.assertEqual(
            str(PostModelTest.post),
            self.post_text_short,
            'Ошибка метода str в модели post при отображении короткого текста'
        )

    def test_str_long_string(self):
        self.assertEqual(
            str(PostModelTest.post_long),
            self.post_text_long[:settings.SHORT_TEXT_LENGTH],
            'Ошибка метода str в модели post при отображении длинного текста'
        )

    def test_verbose_name(self):
        field_verbose_name = {
            'text': 'Текст поста',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verbose_name.items():
            with self.subTest(field=field):
                response = PostModelTest.post._meta.get_field(
                    field
                ).verbose_name
                self.assertEqual(response, expected_value)

    def test_help_text(self):
        field_help_text = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                response = PostModelTest.post._meta.get_field(field).help_text
                self.assertEqual(response, expected_value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_title = 'test_title'
        cls.group = Group.objects.create(
            title=cls.group_title,
            slug='test_slug',
            description='test_description',
        )

    def test_str(self):
        self.assertEqual(
            str(GroupModelTest.group),
            self.group_title,
            'Ошибка метода str в модели group'
        )

    def test_verbose_name(self):
        field_verbose_name = {
            'title': 'Заголовок группы',
            'slug': 'Адрес группы',
            'description': 'Описание группы',
        }
        for field, expected_value in field_verbose_name.items():
            with self.subTest(field=field):
                response = self.group._meta.get_field(field).verbose_name
                self.assertEqual(response, expected_value)

    def test_help_text(self):
        field_help_text = {
            'title': 'Краткое описание группы',
            'slug': 'Используйте только латинские символы, дефисы и знаки '
                    'подчеркивания',
            'description': 'Подробно опишите группу',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                response = self.group._meta.get_field(field).help_text
                self.assertEqual(response, expected_value)
