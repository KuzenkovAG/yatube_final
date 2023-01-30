from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import CommentForm, PostForm
from posts.models import Comment, Follow, Group, Post
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
        cls.follower = User.objects.create_user(username='follow_user')
        Follow.objects.create(
            author=TestViews.user,
            user=TestViews.follower
        )
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
            group=TestViews.group,
            author=TestViews.user,
            text='Текст поста',
            image=uploaded,
        )
        cls.comment = Comment.objects.create(
            author=TestViews.user,
            post=TestViews.post,
            text='Текст тестого комментария'
        )
        cls.urls_template = (
            (
                reverse('posts:index'),
                'posts/index.html'
            ),
            (
                reverse('posts:group_list', args=[TestViews.group.slug]),
                'posts/group_list.html'
            ),
            (
                reverse('posts:profile', args=[TestViews.user.username]),
                'posts/profile.html'
            ),
            (
                reverse('posts:post_detail', args=[TestViews.post.id]),
                'posts/post_detail.html'
            ),
            (
                reverse('posts:post_create'),
                'posts/create_post.html'
            ),
            (
                reverse('posts:post_edit', args=[TestViews.post.id]),
                'posts/create_post.html'
            ),
            (
                reverse('posts:follow_index'),
                'posts/follow.html'
            )
        )
        cls.url_paginator = (
            reverse('posts:index'),
            reverse('posts:group_list', args=[TestViews.group.slug]),
            reverse('posts:profile', args=[TestViews.user.username]),
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(TestViews.user)
        cache.clear()

    def test_used_templates(self):
        """Check used template in all URLs."""
        for address, template in TestViews.urls_template:
            with self.subTest(view=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_context_list_of_posts(self):
        """Check page_obj in URLs with paginator"""
        for url in TestViews.url_paginator:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                first_object = response.context.get('page_obj')[0]
                self.assertEqual(first_object.author, TestViews.post.author)
                self.assertEqual(first_object.group, TestViews.post.group)
                self.assertEqual(first_object.text, TestViews.post.text)
                self.assertEqual(first_object.image, TestViews.post.image)

    def test_follow_page_context(self):
        """Check context of Follow index page."""
        self.follower_client = Client()
        self.follower_client.force_login(TestViews.follower)
        response = self.follower_client.get(reverse('posts:follow_index'))
        first_object = response.context.get('page_obj')[0]
        self.assertEqual(first_object.author, TestViews.post.author)
        self.assertEqual(first_object.group, TestViews.post.group)
        self.assertEqual(first_object.text, TestViews.post.text)
        self.assertEqual(first_object.image, TestViews.post.image)

    def test_post_detail_page_correct_context(self):
        """
        Check context on page of post detail.
        Context: post, comments, post_count, form.
        """
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[TestViews.post.id])
        )
        post = response.context.get('post')
        self.assertEqual(post.id, TestViews.post.id)
        self.assertEqual(post.image, TestViews.post.image)
        post_count = response.context.get('post_count')
        self.assertEqual(post_count, TestViews.user.posts.count())
        comment = response.context.get('comments')[0]
        self.assertEqual(comment, TestViews.comment)
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
            args=[TestViews.post.id]
        ))
        form = response.context.get('form')
        self.assertIsInstance(form, PostForm)
        self.assertTrue(response.context.get('is_edit'))
        self.assertEqual(response.context.get('title'), 'Редактировать пост')


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Группа для теста',
            slug='for_test',
            description='Описание тестовой группы'
        )
        cls.user = User.objects.create_user(username='test_user')
        cls.follower = User.objects.create_user(username='follower')
        Follow.objects.create(
            author=PaginatorTest.user,
            user=PaginatorTest.follower,
        )
        for i in range(1, 14):
            Post.objects.create(
                group=PaginatorTest.group,
                author=PaginatorTest.user,
                text=f'Текст {i}-го поста'
            )
        cls.urls_paginator = (
            reverse('posts:index'),
            reverse('posts:group_list', args=[PaginatorTest.group.slug]),
            reverse('posts:profile', args=[PaginatorTest.user.username]),
            reverse('posts:follow_index')
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorTest.follower)
        cache.clear()

    def test_paginator(self):
        """Inspection of quantity of post on 1st and 2nd page of paginator."""
        for url in PaginatorTest.urls_paginator:
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
            group=TestCreatingPost.group,
            author=TestCreatingPost.user,
            text='Текст поста',
        )
        cls.post = Post.objects.create(
            group=TestCreatingPost.group,
            author=TestCreatingPost.user_another,
            text='Текст созданного другим пользователем',
        )
        cls.post = Post.objects.create(
            group=TestCreatingPost.group_another,
            author=TestCreatingPost.user_another,
            text='Текст созданного другим пользователем в другой группе',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(TestCreatingPost.user)
        cache.clear()

    def test_page_group_correct_posts(self):
        """Page of group show only own group posts."""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[TestCreatingPost.group.slug]))
        posts = response.context.get('page_obj')
        for post in posts:
            self.assertEqual(post.group, TestCreatingPost.group)

    def test_page_profile_correct_posts(self):
        """Page of profile show only own user posts."""
        response = self.authorized_client.get(
            reverse('posts:profile', args=[TestCreatingPost.user.username])
        )
        posts = response.context.get('page_obj')
        for post in posts:
            self.assertEqual(post.author, TestCreatingPost.user)

    def test_post_not_in_other_group(self):
        """Post with other group not show on group page."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            args=[TestCreatingPost.group_another.slug]
        ))
        posts = response.context.get('page_obj')
        for post in posts:
            self.assertNotEqual(post.group, TestCreatingPost.group)


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
        """Delete post and check of index page."""
        response = TestCachePages.guest_client.get(reverse('posts:index'))
        content_before = response.content
        self.post.delete()

        response = TestCachePages.guest_client.get(reverse('posts:index'))
        content_after_remove_post = response.content
        self.assertEqual(
            content_before,
            content_after_remove_post,
            'Cache of Index page not work correctly'
        )

        cache.clear()
        response = TestCachePages.guest_client.get(reverse('posts:index'))
        content_after_clear_cache = response.content
        self.assertNotEqual(
            content_before,
            content_after_clear_cache,
            'Cache of Index page not work correctly'
        )


class TestFollow(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='follower')
        cls.not_follower = User.objects.create_user(username='not_follower')
        cls.author = User.objects.create_user(username='author')
        Follow.objects.create(
            user=TestFollow.follower,
            author=TestFollow.author,
        )

    def setUp(self):
        self.follower_client = Client()
        self.follower_client.force_login(TestFollow.follower)
        self.unfollower_client = Client()
        self.unfollower_client.force_login(TestFollow.not_follower)

    def test_remove_following_add_following(self):
        """Check correctly working Follow and Unfollow."""
        initial_follows_count = Follow.objects.count()
        self.follower_client.get(reverse(
            'posts:profile_unfollow',
            args=[TestFollow.author]
        ))
        self.assertEqual(
            Follow.objects.count(),
            initial_follows_count - 1,
            'Unfollow from user not work correctly'
        )
        initial_follows_count = Follow.objects.count()
        self.follower_client.get(reverse(
            'posts:profile_follow',
            args=[TestFollow.author]
        ))
        self.assertEqual(
            Follow.objects.count(),
            initial_follows_count + 1,
            'Follow to user not work correctly'
        )

    def test_new_post_can_see_only_follower(self):
        """Author post can see only Followers and can't others."""
        post = Post.objects.create(
            author=TestFollow.author,
            text='This post can see only my followers'
        )
        response = self.follower_client.get(reverse('posts:follow_index'))
        page = response.context.get('page_obj')
        self.assertIn(post, page, 'Follower not see new post')
        response = self.unfollower_client.get(reverse('posts:follow_index'))
        page = response.context.get('page_obj')
        self.assertNotIn(post, page, 'User what not follow see new post')
