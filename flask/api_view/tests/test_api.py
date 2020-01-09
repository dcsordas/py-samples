from http import HTTPStatus
import unittest

from flask import Flask

from api_view import api
from api_view import db_setup
from lib import util


# base classes
class BaseApiTestCase(unittest.TestCase):
    """API test case parent class."""
    test_api = None
    test_client = None

    def setUp(self):
        app = Flask('test')
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.test_api = api.ApiServer(app)
        self.test_client = app.test_client()


class BaseApiTestCaseWithDB(BaseApiTestCase):
    """API test case parent class with in-memory database fixture."""
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
        self.test_source = util.DataSource(connection)

    def tearDown(self):
        del self.test_source


# test classes
class TestApiRoot(BaseApiTestCase):
    """API root end point responses."""

    def setUp(self):
        super(TestApiRoot, self).setUp()
        api.RootView.register_view(self.test_api.app, source=None)

    def test_HEADER(self):
        actual = self.test_client.head('/')
        self.assertEqual(
            (actual.json, actual.status_code),
            (None, HTTPStatus.NO_CONTENT))


class TestApiData(BaseApiTestCaseWithDB):
    """API /data end point responses."""

    def setUp(self):
        super(TestApiData, self).setUp()
        api.DataView.register_view(self.test_api.app, self.test_source)

    def test_data_GET(self):
        actual = self.test_client.get('/data')
        expected_json = dict(ids=[1, 2])
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.OK))

    def test_data_GET__ok(self):
        actual = self.test_client.get('/data/1')
        expected_json = dict(data=dict(name='one', username='test1', email='test1@example.com'))
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.OK))

    def test_data_GET__not_found(self):
        actual = self.test_client.get('/data/3')
        expected_json = dict(error='Not found')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.NOT_FOUND))

    def test_data_POST__ok(self):
        data = dict(name='three', username='test3', email='test3@example.com')
        actual = self.test_client.post(
            '/data', json=dict(data=data))
        expected_json = dict(id=3)
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.CREATED))

    def test_data_POST__no_data(self):
        data = None
        actual = self.test_client.post('/data', json=dict(data=data))
        expected_json = dict(error='No data')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.BAD_REQUEST))

    def test_data_POST__partial_data(self):
        data = dict(name='fail')
        actual = self.test_client.post('/data', json=dict(data=data))
        expected_json = dict(error='NOT NULL constraint failed: user_data.username')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.INTERNAL_SERVER_ERROR))

    def test_data_PUT__ok(self):
        data = dict(name='neo', username='1test', email='test1@example.org')
        actual = self.test_client.put('/data/1', json=dict(data=data))
        self.assertEqual(
            (actual.json, actual.status_code),
            (None, HTTPStatus.NO_CONTENT))

    def test_data_PUT__no_data(self):
        data = None
        actual = self.test_client.put('/data/1', json=dict(data=data))
        expected_json = dict(error='No data')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.BAD_REQUEST))

    def test_data_PUT__partial_data(self):
        data = dict(name='fail')
        actual = self.test_client.put('/data/1', json=dict(data=data))
        expected_json = dict(error='NOT NULL constraint failed: user_data.username')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.INTERNAL_SERVER_ERROR))

    def test_data_PUT__not_found(self):
        data = dict(name='three', username='test3', email='test3@example.com')
        actual = self.test_client.put('/data/3', json=dict(data=data))
        expected_json = dict(error='UPDATE failed')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.INTERNAL_SERVER_ERROR))

    def test_data_DELETE__ok(self):
        actual = self.test_client.delete('/data/1')
        self.assertEqual(
            (actual.json, actual.status_code),
            (None, HTTPStatus.NO_CONTENT))

    def test_data_DELETE__not_found(self):
        actual = self.test_client.delete('/data/3')
        expected_json = dict(error='DELETE failed')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.INTERNAL_SERVER_ERROR))
