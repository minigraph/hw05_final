from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from posts.tests.test_urls import get_status_user


User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')

    def setUp(self):
        self.guest_client = Client()
        self.user_client = Client()
        self.user_client.force_login(UsersURLTests.user)

    def test_urls_all(self):
        """Проверяем доступ к страницам url"""
        urls_name_status = {
            '/auth/logout/': get_status_user(HTTPStatus.OK),
            '/auth/signup/': get_status_user(HTTPStatus.OK),
            '/auth/login/': get_status_user(HTTPStatus.OK),
            '/auth/change_pwd/': get_status_user(HTTPStatus.FOUND,
                                                 HTTPStatus.FOUND),
        }
        for url, dict_status in urls_name_status.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, dict_status['guest'])
                response = self.user_client.get(url)
                self.assertEqual(response.status_code, dict_status['user'])
