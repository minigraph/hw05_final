import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..forms import PostForm, CommentForm
from ..models import Post, Group, Comment


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


def get_data_for_new_post():
    return {
        'posts_count': Post.objects.count(),
        'form_data': {
            'text': 'Тестовый текст',
            'group': PostCreateFormTests.group.id,
            'image': PostCreateFormTests.uploaded.name,
            'image_path': 'posts/small.gif',
        }
    }


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            id=1,
            author=cls.user,
            text='Тестовый пост',
            image=cls.uploaded,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(PostCreateFormTests.user)

    def test_create_post_for_guest_client(self):
        data_post = get_data_for_new_post()
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=data_post['form_data'],
        )
        self.assertRedirects(
            response, reverse('users:login') + '?next=/create/'
        )
        self.assertEqual(Post.objects.count(), data_post['posts_count'])
        self.assertFalse(
            Post.objects.filter(
                id=2,
                text=data_post['form_data']['text'],
                group=data_post['form_data']['group'],
                image=data_post['form_data']['image_path']
            ).exists()
        )

    def test_create_post_for_auth_client(self):
        data_post = get_data_for_new_post()
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=data_post['form_data'],
        )
        self.assertRedirects(
            response, reverse('posts:profile', kwargs={'username': 'user'})
        )
        self.assertEqual(Post.objects.count(), data_post['posts_count'] + 1)
        self.assertTrue(
            Post.objects.filter(
                id=2,
                text=data_post['form_data']['text'],
                group=data_post['form_data']['group']
            ).exists()
        )

    def test_edit_post_for_guest_client(self):
        data_post = get_data_for_new_post()
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=data_post['form_data']
        )
        self.assertRedirects(
            response, reverse('users:login') + '?next=/posts/1/edit/'
        )
        self.assertFalse(
            Post.objects.filter(
                id=1,
                text=data_post['form_data']['text'],
                group=data_post['form_data']['group'],
                image=data_post['form_data']['image_path']
            ).exists()
        )

    def test_edit_post_for_auth_client(self):
        data_post = get_data_for_new_post()
        response = self.auth_client.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=data_post['form_data']
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', kwargs={'post_id': 1})
        )
        self.assertTrue(
            Post.objects.filter(
                id=1,
                text=data_post['form_data']['text'],
                group=data_post['form_data']['group'],
                image=data_post['form_data']['image_path']
            ).exists()
        )


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.post = Post.objects.create(
            id=1,
            author=cls.user,
            text='Тестовый пост',
        )
        cls.form = CommentForm()

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(CommentCreateFormTests.user)

    def test_create_comment_for_guest_client(self):
        data_comment = {
            'count': Comment.objects.count(),
            'form_data': {
                'text': 'Тестовый текст',
            }
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': 1}),
            data=data_comment['form_data'],
        )
        self.assertRedirects(
            response, reverse('users:login') + '?next=/posts/1/comment/'
        )
        self.assertEqual(Comment.objects.count(), data_comment['count'])
        self.assertFalse(
            Comment.objects.filter(
                id=1,
                text=data_comment['form_data']['text'],
            ).exists()
        )

    def test_create_comment_for_auth_client(self):
        data_comment = {
            'count': Comment.objects.count(),
            'form_data': {
                'text': 'Тестовый текст',
            }
        }
        response = self.auth_client.post(
            reverse('posts:add_comment', kwargs={'post_id': 1}),
            data=data_comment['form_data'],
        )
        self.assertRedirects(
            response, reverse('posts:post_detail', kwargs={'post_id': 1})
        )
        self.assertEqual(Comment.objects.count(), data_comment['count'] + 1)
        self.assertTrue(
            Comment.objects.filter(
                id=1,
                text=data_comment['form_data']['text'],
            ).exists()
        )
