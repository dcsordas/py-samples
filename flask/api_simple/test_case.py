from http import HTTPStatus
import unittest
from unittest import mock

from api_simple import api
from api_simple import db_setup
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
            connection.execute(db_setup.SQL_CREATE_TABLE_USER_DATA)
        with connection:
            connection.executemany(
                "INSERT INTO user_data (name, username, email) VALUES (?, ?, ?)",
                (
                    ('one', 'test1', 'test1@example.com'),
                    ('two', 'test2', 'test2@example.com'),
                )
            )
        self.test_connection = connection
        self.test_source = util.DataSource(connection)

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


class TestApiData(BaseApiTestCaseWithDB):
    """API /data end point responses."""

    def test_data_GET(self):
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.test_app.get('/data')
        expected_json = dict(ids=[1, 2])
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.OK))

    def test_data_GET__ok(self):
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.test_app.get('/data/1')
        expected_json = dict(data=dict(name='one', username='test1', email='test1@example.com'))
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.OK))

    def test_data_GET__not_found(self):
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.test_app.get('/data/3')
        expected_json = dict(error='Not found')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.NOT_FOUND))

    def test_data_POST__ok(self):
        data = dict(name='three', username='test3', email='test3@example.com')
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.test_app.post(
                '/data', json=dict(data=data))
        expected_json = dict(id=3)
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.CREATED))

    def test_data_POST__no_data(self):
        data = None
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.test_app.post('/data', json=dict(data=data))
        expected_json = dict(error='No data')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.BAD_REQUEST))

    def test_data_POST__partial_data(self):
        data = dict(name='fail')
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.test_app.post('/data', json=dict(data=data))
        expected_json = dict(error='NOT NULL constraint failed: user_data.username')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.INTERNAL_SERVER_ERROR))

    def test_data_PUT__ok(self):
        data = dict(name='neo', username='1test', email='test1@example.org')
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.test_app.put('/data/1', json=dict(data=data))
        self.assertEqual(
            (actual.json, actual.status_code),
            (None, HTTPStatus.NO_CONTENT))

    def test_data_PUT__no_data(self):
        data = None
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.test_app.put('/data/1', json=dict(data=data))
        expected_json = dict(error='No data')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.BAD_REQUEST))

    def test_data_PUT__partial_data(self):
        data = dict(name='fail')
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.test_app.put('/data/1', json=dict(data=data))
        expected_json = dict(error='NOT NULL constraint failed: user_data.username')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.INTERNAL_SERVER_ERROR))

    def test_data_PUT__not_found(self):
        data = dict(name='three', username='test3', email='test3@example.com')
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.test_app.put('/data/3', json=dict(data=data))
        expected_json = dict(error='UPDATE failed')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.INTERNAL_SERVER_ERROR))

    def test_data_DELETE__ok(self):
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.test_app.delete('/data/1')
        self.assertEqual(
            (actual.json, actual.status_code),
            (None, HTTPStatus.NO_CONTENT))

    def test_data_DELETE__not_found(self):
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.test_app.delete('/data/3')
        expected_json = dict(error='DELETE failed')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.INTERNAL_SERVER_ERROR))
