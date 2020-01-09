from requests.auth import _basic_auth_str

from http import HTTPStatus
import unittest
from unittest import mock
import uuid

from api_basic_auth import api
from api_basic_auth import setup_db
from lib import util


# base classes
class BaseApiTestCase(unittest.TestCase):
    """API test case parent class."""
    test_app = None

    @classmethod
    def setUpClass(cls):
        api.app.config['TESTING'] = True
        api.app.config['DEBUG'] = False

    def setUp(self):
        self.test_app = api.app.test_client()


class BaseApiTestCaseWithDB(BaseApiTestCase):
    """API test case parent class with in-memory database fixture."""
    test_connection = None
    test_source = None

    def setUp(self):
        super(BaseApiTestCaseWithDB, self).setUp()

        # set up database
        connection = util.get_connection(':memory:')
        with connection:
            connection.execute(setup_db.SQL_CREATE_TABLE_USER_CREDENTIALS)
        with connection:
            values = []
            for username, password in [('test1', 'pw1'), ('test2', 'pw2')]:
                salt = str(uuid.uuid4())
                values.append([username, api.hash_password(password, salt), salt])
            connection.executemany("""
                INSERT INTO user_credentials (
                  username,
                  password_hash,
                  password_salt)
                VALUES (?, ?, ?) """, values)
        self.test_connection = connection
        self.test_source = util.CredentialsSource(connection)

    def tearDown(self):
        del self.test_source


# test classes
class TestApiRoot(BaseApiTestCase):
    """API root end point responses."""

    def test_HEADER(self):
        actual = self.test_app.head('/')
        self.assertEqual(
            (actual.json, actual.status_code),
            (None, HTTPStatus.NO_CONTENT))


class TestApiUsers(BaseApiTestCaseWithDB):
    """API /users end point responses."""

    def test_users_GET__ok(self):
        username = 'test1'
        password = 'pw1'
        with mock.patch('api_basic_auth.api.source', self.test_source):
            actual = self.test_app.get('/users', headers={"Authorization": _basic_auth_str(username, password)})
        self.assertEqual(
            (actual.get_json(), actual.status_code),
            (dict(usernames=['test1', 'test2']), HTTPStatus.OK))

    def test_users_GET__unauthenticated(self):
        with mock.patch('api_basic_auth.api.source', self.test_source):
            actual = self.test_app.get('/users')
        self.assertEqual(
            (actual.data, actual.status_code),
            (b'Unauthorized Access', HTTPStatus.UNAUTHORIZED))

    def test_users_GET__unauthorized(self):
        username = 'not_a_user'
        password = 'not_a_password'
        with mock.patch('api_basic_auth.api.source', self.test_source):
            actual = self.test_app.get('/users', headers={"Authorization": _basic_auth_str(username, password)})
        self.assertEqual(
            (actual.data, actual.status_code),
            (b'Unauthorized Access', HTTPStatus.UNAUTHORIZED))

    def test_users_POST__ok(self):
        username = 'test_user'
        password = 'test_password'
        with mock.patch('api_basic_auth.api.source', self.test_source):
            actual = self.test_app.post('/users', data=dict(username=username, password=password))
        self.assertEqual(
            (actual.data, actual.status_code, self.test_source.has_username(username)),
            (b'', HTTPStatus.CREATED, True))

    def test_users_POST__missing_username(self):
        data = dict(password='test_password')
        with mock.patch('api_basic_auth.api.source', self.test_source):
            actual = self.test_app.post('/users', data=data)
        self.assertEqual(
            (actual.get_json(), actual.status_code),
            (data, HTTPStatus.UNPROCESSABLE_ENTITY))

    def test_users_POST__missing_password(self):
        username = 'test_user'
        data = dict(username=username)
        with mock.patch('api_basic_auth.api.source', self.test_source):
            actual = self.test_app.post('/users', data=data)
        self.assertEqual(
            (actual.get_json(), actual.status_code, self.test_source.has_username(username)),
            (data, HTTPStatus.UNPROCESSABLE_ENTITY, False))
