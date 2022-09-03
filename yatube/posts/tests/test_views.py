import shutil
import tempfile


from xmlrpc.client import Boolean
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..models import Post, Group, Follow


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
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
        cls.auth_user = User.objects.create_user(username='auth_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            id=1,
            author=cls.auth_user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(PostPagesTests.auth_user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'group-slug'}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'auth_user'}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': 1}):
            'posts/post_detail.html',
            reverse('posts:post_create'): {
                'auth': 'posts/create_edit_post.html',
            },
            reverse('posts:post_edit', kwargs={'post_id': 1}): {
                'auth': 'posts/create_edit_post.html',
            },
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                if isinstance(template, str):
                    response = self.auth_client.get(reverse_name)
                    self.assertTemplateUsed(response, template)
                else:
                    template = template['auth']

                response = self.auth_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        pages_names_context = {
            reverse('posts:post_detail', kwargs={'post_id': 1}): {
                'post': Post,
            },
            reverse('posts:post_create'): {
                'form': {
                    'text': forms.fields.CharField,
                    'group': forms.models.ModelChoiceField,
                    'image': forms.fields.ImageField,
                },
            },
            reverse('posts:post_edit', kwargs={'post_id': 1}): {
                'form': {
                    'text': forms.fields.CharField,
                    'group': forms.models.ModelChoiceField,
                    'image': forms.fields.ImageField,
                },
                'post': Post,
                'is_edit': Boolean,
            },
        }

        for page_name, page_context in pages_names_context.items():
            with self.subTest(page_name=page_name):
                response = self.auth_client.get(page_name)
                for value, expected in page_context.items():
                    if value != 'form':
                        f_field = response.context.get(value)
                        self.assertIsInstance(f_field, expected)
                        continue

                    for key, exp in expected.items():
                        f_field = response.context.get('form').fields.get(key)
                        self.assertIsInstance(f_field, exp)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.auth_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, PostPagesTests.auth_user)
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertEqual(post_group_0, PostPagesTests.group)
        self.assertEqual(post_image_0, PostPagesTests.post.image)

    def test_group_page_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.auth_client.get(
            reverse('posts:group_list', kwargs={'slug': 'group-slug'})
        )
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, PostPagesTests.auth_user)
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertEqual(post_group_0, PostPagesTests.group)
        self.assertEqual(post_image_0, PostPagesTests.post.image)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.auth_client.get(
            reverse('posts:profile', kwargs={'username': 'auth_user'})
        )
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, PostPagesTests.auth_user)
        self.assertEqual(post_text_0, 'Тестовый пост')
        self.assertEqual(post_group_0, PostPagesTests.group)
        self.assertEqual(post_image_0, PostPagesTests.post.image)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create_user(username='auth_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group-slug',
            description='Тестовое описание',
        )
        Post.objects.bulk_create(
            [Post(
                id=1 + i,
                author=cls.auth_user,
                text='Пост' + str(i),
                group=cls.group
            ) for i in range(13)]
        )

    def setUp(self):
        self.client = Client()

    def test_first_second_page_contains(self):
        reverse_pages_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'group-slug'}),
            reverse('posts:profile', kwargs={'username': 'auth_user'}),
        ]
        for reverse_name in reverse_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']), 10)
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_user = User.objects.create_user(username='auth_user')
        cls.author = User.objects.create_user(username='author')
        cls.new_author = User.objects.create_user(username='author')
        Post.objects.create(
            id=1,
            author=cls.author,
            text='Тестовый пост'
        )

    def setUp(self):
        Follow.objects.create(
            user=FollowViewsTest.auth_user,
            author=FollowViewsTest.author,
        )
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(FollowViewsTest.auth_user)
        self.author = Client()
        self.author.force_login(FollowViewsTest.author)

    def test_profile_follow_correct(self):
        count_follow = Follow.objects.count()
        reverse_name = reverse(
            'posts:profile_follow',
            kwargs={'username': 'new_author'}
        )
        response = self.guest_client.post(reverse_name)
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=/profile/new_author/follow/'
        )
        self.assertEqual(Follow.objects.count(), count_follow)
        self.assertFalse(
            Follow.objects.filter(
                user=FollowViewsTest.auth_user,
                author=FollowViewsTest.new_author
            ).exists()
        )

        response = self.auth_client.post(reverse_name)
        self.assertRedirects(
            response, reverse(
                'posts:profile',
                kwargs={'username': 'new_author'}
            )
        )
        self.assertEqual(Follow.objects.count(), count_follow + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=FollowViewsTest.auth_user,
                author=FollowViewsTest.new_author
            ).exists()
        )

    def test_profile_unfollow_correct(self):
        count_follow = Follow.objects.count()
        reverse_name = reverse(
            'posts:profile_unfollow',
            kwargs={'username': 'author'}
        )
        response = self.guest_client.post(reverse_name)
        self.assertRedirects(
            response,
            reverse('users:login') + '?next=/profile/author/unfollow/'
        )
        self.assertEqual(Follow.objects.count(), count_follow)
        self.assertTrue(
            Follow.objects.filter(
                user=FollowViewsTest.auth_user,
                author=FollowViewsTest.author
            ).exists()
        )

        response = self.auth_client.post(reverse_name)
        self.assertRedirects(
            response, reverse(
                'posts:profile',
                kwargs={'username': 'author'}
            )
        )
        self.assertEqual(Follow.objects.count(), count_follow - 1)
        self.assertFalse(
            Follow.objects.filter(
                user=FollowViewsTest.auth_user,
                author=FollowViewsTest.author
            ).exists()
        )

    def test_follow_correct_context(self):
        response = self.auth_client.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        self.assertEqual(post_author_0, FollowViewsTest.author)
        self.assertEqual(post_text_0, 'Тестовый пост')

        response = self.author.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'].object_list
        self.assertEqual(0, len(first_object))
