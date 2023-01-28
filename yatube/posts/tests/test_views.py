from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import CommentForm, PostForm
from posts.models import Comment, Group, Post
import shutil
import tempfile

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа для теста',
            slug='for_test',
            description='Описание тестовой группы'
        )
        cls.user = User.objects.create_user(username='test_user')
        image_png = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.png',
            content=image_png,
            content_type='image/png'
        )
        cls.post = Post.objects.create(
            group=cls.group,
            author=cls.user,
            text='Текст поста',
            image=uploaded,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Текст тестого комментария'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_used_templates(self):
        templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                args=[self.group.slug]
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                args=[self.user.username]
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                args=[self.post.id]
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                args=[self.post.id]
            ): 'posts/create_post.html',
        }
        for address, template in templates.items():
            with self.subTest(view=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_context_list_of_posts(self):
        """Check post lists"""
        url = [
            reverse('posts:index'),
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user.username]),
        ]
        for url in url:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                first_object = response.context.get('page_obj')[0]
                self.assertEqual(first_object.author, self.post.author)
                self.assertEqual(first_object.group, self.post.group)
                self.assertEqual(first_object.text, self.post.text)
                self.assertEqual(first_object.image, self.post.image)

    def test_post_detail_page_correct_context(self):
        """
        Context on page of post detail.
        Context: post, comments, post_count
        """
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[self.post.id])
        )
        post = response.context.get('post')
        self.assertEqual(post.id, self.post.id)
        self.assertEqual(post.image, self.post.image)
        post_count = response.context.get('post_count')
        self.assertEqual(post_count, self.user.posts.count())
        comment = response.context.get('comments')[0]
        self.assertEqual(comment, self.comment)

    def test_page_detail_post_from_comment(self):
        """Inspection of comment form on post detail page."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[self.post.id])
        )
        form = response.context.get('form')
        self.assertIsInstance(form, CommentForm)
        text_field = form.fields.get('text')
        self.assertIsInstance(text_field, forms.fields.CharField)

    def test_page_creating_post(self):
        """Check context of page for create post."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm)
        self.assertEqual(response.context.get('title'), 'Новый пост')

    def test_page_edit_post(self):
        """Check context of page for edit post."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            args=[self.post.id]
        ))
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm)
        self.assertTrue(response.context.get('is_edit'))
        self.assertEqual(response.context.get('title'), 'Редактировать пост')


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа для теста',
            slug='for_test',
            description='Описание тестовой группы'
        )
        cls.user = User.objects.create_user(username='test_user')
        for i in range(1, 14):
            Post.objects.create(
                group=cls.group,
                author=cls.user,
                text=f'Текст {i}-го поста'
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_paginator(self):
        """Inspection of quantity of post on 1st and 2nd page of paginator."""
        urls = [
            reverse('posts:index'),
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user.username]),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.max_post_on_page = settings.POST_LIMIT_ON_PAGE
                self.check_objects_on_first_page(url)
                self.check_objects_on_second_page(url)

    def check_objects_on_first_page(self, url):
        """Inspection of quantity of post on 1st page of paginator."""
        self.assertEqual(self.quantity_of_posts(url), self.max_post_on_page)

    def check_objects_on_second_page(self, url):
        """Inspection of quantity of post on 2nd page of paginator."""
        url = url + '?page=2'
        post_quantity = 3
        self.assertEqual(self.quantity_of_posts(url), post_quantity)

    def quantity_of_posts(self, url):
        """Quantity of posts on page received by url."""
        response = self.authorized_client.get(url)
        return len(response.context.get('page_obj'))


class TestCreatingPost(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа для теста',
            slug='group',
            description='Описание тестовой группы'
        )
        cls.group_another = Group.objects.create(
            title='Группа для теста',
            slug='group_another',
            description='Другая тестовой группы'
        )

        cls.user = User.objects.create_user(username='test_user')
        cls.user_another = User.objects.create_user(username='User_another')
        cls.post = Post.objects.create(
            group=cls.group,
            author=cls.user,
            text='Текст поста',
        )
        cls.post = Post.objects.create(
            group=cls.group,
            author=cls.user_another,
            text='Текст созданного другим пользователем',
        )
        cls.post = Post.objects.create(
            group=cls.group_another,
            author=cls.user_another,
            text='Текст созданного другим пользователем в другой группе',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_page_group_correct_posts(self):
        """Page of group show only own group posts."""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[self.group.slug]))
        posts = response.context.get('page_obj')
        for post in posts:
            self.assertEqual(post.group, self.group)

    def test_page_profile_correct_posts(self):
        """Page of profile show only own user posts."""
        response = self.authorized_client.get(
            reverse('posts:profile', args=[self.user.username])
        )
        posts = response.context.get('page_obj')
        for post in posts:
            self.assertEqual(post.author, self.user)

    def test_post_not_in_other_group(self):
        """Post with other group not show on group page."""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[self.group_another.slug])
        )
        posts = response.context.get('page_obj')
        for post in posts:
            self.assertNotEqual(post.group, self.group)


class TestCachePages(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='testuser')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Post what will be delete',
        )

    def setUp(self):
        cache.clear()

    def test_cache_index_page(self):
        """Delete post and check cache of index page."""
        response = self.guest_client.get(reverse('posts:index'))
        content_before = response.content
        self.post.delete()
        response = self.guest_client.get(reverse('posts:index'))
        content_after_remove_post = response.content
        self.assertEqual(
            content_before,
            content_after_remove_post,
            'Cache of Index page not work correctly'
        )
        cache.clear()
        response = self.guest_client.get(reverse('posts:index'))
        content_after_clear_cache = response.content
        self.assertNotEqual(
            content_before,
            content_after_clear_cache,
            'Cache of Index page not work correctly'
        )
