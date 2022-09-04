from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache
from http import HTTPStatus
from ..models import Post, Group


User = get_user_model()


def get_status_user(*args) -> dict:
    """Функция возвращает общий статус, если передан один аргумент,
    индивидуальный статус, если два или три аргумента"""
    if len(args) == 1:
        return {
            'guest': args[0],
            'user': args[0],
            'auth': args[0],
        }
    elif len(args) == 2:
        return {
            'guest': args[0],
            'user': args[1],
        }
    elif len(args) == 3:
        return {
            'guest': args[0],
            'user': args[1],
            'auth': args[2],
        }


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        """Дымовой тест, доступна страница /"""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='author')
        cls.auth = User.objects.create_user(username='auth')
        cls.smb_user = User.objects.create_user(username='smb_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='group-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            id=1,
            author=cls.auth,
            text='Тестовый пост',
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.smb_user_client = Client()
        self.smb_user_client.force_login(PostsURLTests.smb_user)
        self.auth_client = Client()
        self.auth_client.force_login(PostsURLTests.auth)

    def test_urls_all(self):
        """Проверяем доступ к страницам url"""
        urls_name_status = {
            '/': get_status_user(HTTPStatus.OK),
            '/group/group-slug/': get_status_user(HTTPStatus.OK),
            '/profile/auth/': get_status_user(HTTPStatus.OK),
            '/posts/1/': get_status_user(HTTPStatus.OK),
            '/create/': get_status_user(HTTPStatus.FOUND,
                                        HTTPStatus.OK,
                                        HTTPStatus.OK),
            '/posts/1/edit/': get_status_user(HTTPStatus.FOUND,
                                              HTTPStatus.FOUND,
                                              HTTPStatus.OK),
            '/unknown_page/': get_status_user(HTTPStatus.NOT_FOUND),
            '/posts/1/comment/': get_status_user(HTTPStatus.FOUND,
                                                 HTTPStatus.FOUND,
                                                 HTTPStatus.FOUND),
            '/follow/': get_status_user(HTTPStatus.FOUND,
                                        HTTPStatus.OK,
                                        HTTPStatus.OK),
            '/profile/author/follow/': get_status_user(HTTPStatus.FOUND,
                                                       HTTPStatus.FOUND,
                                                       HTTPStatus.FOUND),
            '/profile/author/unfollow/': get_status_user(HTTPStatus.FOUND,
                                                         HTTPStatus.FOUND,
                                                         HTTPStatus.FOUND),
        }
        for url, dict_status in urls_name_status.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, dict_status['guest'])
                response = self.smb_user_client.get(url)
                self.assertEqual(response.status_code, dict_status['user'])
                response = self.auth_client.get(url)
                self.assertEqual(response.status_code, dict_status['auth'])

    def test_templates(self):
        """Проверям соответствие url-страницы шаблону"""
        urls_templates_name_for_guest = {
            '/': 'posts/index.html',
            '/group/group-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
        }
        for url, template in urls_templates_name_for_guest.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

        cache.clear()
        urls_templates_name_for_user = {
            '/': 'posts/index.html',
            '/group/group-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_edit_post.html',
            '/follow/': 'posts/follow.html',
        }
        for url, template in urls_templates_name_for_user.items():
            with self.subTest(url=url):
                response = self.smb_user_client.get(url)
                self.assertTemplateUsed(response, template)

        cache.clear()
        urls_templates_name_for_auth = {
            '/': 'posts/index.html',
            '/group/group-slug/': 'posts/group_list.html',
            '/profile/auth/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_edit_post.html',
            '/posts/1/edit/': 'posts/create_edit_post.html',
            '/follow/': 'posts/follow.html',
        }
        for url, template in urls_templates_name_for_auth.items():
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertTemplateUsed(response, template)
