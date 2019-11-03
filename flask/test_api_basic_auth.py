from http import HTTPStatus
from requests.auth import _basic_auth_str
import unittest
from unittest import mock

import api_basic_auth
from lib import util


class TestApiBasicAuth(unittest.TestCase):
    """REST API responses."""

    test_app = None

    @classmethod
    def setUpClass(cls):
        api_basic_auth.app.config['TESTING'] = True
        api_basic_auth.app.config['DEBUG'] = False

    def setUp(self):
        self.test_app = api_basic_auth.app.test_client()

    def test_root(self):
        actual = self.test_app.head('/')
        self.assertEqual(
            (actual.data, actual.status_code),
            (b'', HTTPStatus.NO_CONTENT))

    def test_list_users(self):
        username = 'test_user'
        password = 'test_password'
        source = self.get_source()
        source.set_credentials(username, util.hash_password(password))
        with mock.patch('api_basic_auth.source', source):
            actual = self.test_app.get('/users', headers={"Authorization": _basic_auth_str(username, password)})
        self.assertEqual(
            (actual.get_json(), actual.status_code),
            (dict(usernames=[username]), HTTPStatus.OK))

    def test_list_users__unauthenticated(self):
        with mock.patch('api_basic_auth.source', self.get_source()):
            actual = self.test_app.get('/users')
        self.assertEqual(
            (actual.data, actual.status_code),
            (b'Unauthorized Access', HTTPStatus.UNAUTHORIZED))

    def test_list_users__unauthorized(self):
        username = 'test_user'
        password = 'test_password'
        with mock.patch('api_basic_auth.source', self.get_source()):
            actual = self.test_app.get('/users', headers={"Authorization": _basic_auth_str(username, password)})
        self.assertEqual(
            (actual.data, actual.status_code),
            (b'Unauthorized Access', HTTPStatus.UNAUTHORIZED))

    def test_register_user(self):
        username = 'test_user'
        password = 'test_password'
        source = self.get_source()
        with mock.patch('api_basic_auth.source', source):
            actual = self.test_app.post('/users', data=dict(username=username, password=password))
        self.assertEqual(
            (actual.data, actual.status_code, source.has_username(username)),
            (b'', HTTPStatus.CREATED, True))

    def test_register_user__missing_username(self):
        data = dict(password='test_password')
        source = self.get_source()
        with mock.patch('api_basic_auth.source', source):
            actual = self.test_app.post('/users', data=data)
        self.assertEqual(
            (actual.get_json(), actual.status_code),
            (data, HTTPStatus.UNPROCESSABLE_ENTITY))

    def test_register_user__missing_password(self):
        username = 'test_user'
        data = dict(username=username)
        source = self.get_source()
        with mock.patch('api_basic_auth.source', source):
            actual = self.test_app.post('/users', data=data)
        self.assertEqual(
            (actual.get_json(), actual.status_code, source.has_username(username)),
            (data, HTTPStatus.UNPROCESSABLE_ENTITY, False))

    @staticmethod
    def get_source():
        """CredentialsSource provider."""
        return util.CredentialsSource()
