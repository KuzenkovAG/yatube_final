import shutil
import tempfile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import CommentForm, PostForm
from posts.models import Comment, Group, Post


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


def get_posts_count():
    return Post.objects.count()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestForms(TestCase):
    """Checking form PostForm for create and edit posts"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.form = PostForm()
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_group',
            description='Group for test',
        )
        cls.another_group = Group.objects.create(
            title='Another group',
            slug='another_group',
            description='Group for changing during edit post',
        )
        cls.post = Post.objects.create(
            group=cls.group,
            text='Post to edit',
            author=cls.user
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_creating_post(self):
        """Checking creating new post."""
        initial_post_count = get_posts_count()
        image_png = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='image.png',
            content=image_png,
            content_type='image/png'
        )
        form_content = {
            'group': self.group.pk,
            'text': 'It is test post',
            'image': uploaded,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_content,
            folow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            args=[self.user.username]
        ))
        self.assertEqual(
            get_posts_count(),
            initial_post_count + 1,
            'Post was not created'
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_content.get('text'),
                group=form_content.get('group'),
                image='posts/image.png',
            ).exists(),
            'Post was not created correctly'
        )

    def test_post_edit(self):
        """Checking edition existing post."""
        initial_post_count = get_posts_count()
        form_content = {
            'text': 'Post was edited',
            'group': self.another_group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_content,
            folow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            args=[self.post.id]
        ))
        self.assertEqual(
            get_posts_count(),
            initial_post_count,
            'Changed amount of Posts'
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_content.get('text'),
                group=form_content.get('group'),
            ).exists(),
            'Post not edited'
        )


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.form = CommentForm()
        cls.post = Post.objects.create(
            author=cls.user,
            text='Its test post'
        )

    def test_creating_comment(self):
        """Creating comment and check it in bd."""
        initial_comments_count = self.post.comments.count()
        form_content = {
            'text': 'It is test comment',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            data=form_content,
            folow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            args=[self.post.id]
        ))
        self.assertEqual(
            self.post.comments.count(),
            initial_comments_count + 1,
            'Comment not created'
        )
        self.assertTrue(
            Comment.objects.filter(
                text=form_content.get('text'),
            ).exists(),
            'Comment created not correctly'
        )
