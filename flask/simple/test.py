from http import HTTPStatus
import unittest
from unittest import mock

from simple import api
from lib import util


class TestSimpleApi(unittest.TestCase):
    """REST API responses."""

    test_app = None

    @classmethod
    def setUpClass(cls):
        api.app.config['TESTING'] = True
        api.app.config['DEBUG'] = False

    def setUp(self):
        self.test_app = api.app.test_client()

    def test_root(self):
        actual = self.test_app.head('/')
        self.assertEqual(
            (actual.data, actual.status_code),
            (b'', HTTPStatus.NO_CONTENT))

    def test_data__get_ids(self):
        with mock.patch('simple.api.source', self.get_source()):
            actual = self.test_app.get('/data')
        expected_json = dict(ids=[0, 1])
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.OK))

    def test_data__get_data(self):
        with mock.patch('simple.api.source', self.get_source()):
            actual = self.test_app.get('/data/0')
        expected_json = dict(id=0, data='alpha')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.OK))

    def test_data__get_data__not_found(self):
        with mock.patch('simple.api.source', self.get_source()):
            actual = self.test_app.get('/data/2')
        expected_json = dict(id=2)
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.NOT_FOUND))

    def test_data__create_data(self):
        with mock.patch('simple.api.source', self.get_source()):
            actual = self.test_app.post('/data', json=dict(data='gamma'))
        expected_json = dict(id=2)
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.CREATED))

    def test_data__create_data__malformed(self):
        data = '{'
        with mock.patch('simple.api.source', self.get_source()):
            actual = self.test_app.post('/data', json=data)
        expected_json = dict(data=data)
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.BAD_REQUEST))

    def test_data__create_data__no_data(self):
        data = dict(test='fail')
        with mock.patch('simple.api.source', self.get_source()):
            actual = self.test_app.post('/data', json=data)
        expected_json = dict(data=data)
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.BAD_REQUEST))

    def test_data__update_data(self):
        data = dict(data='gamma')
        with mock.patch('simple.api.source', self.get_source()):
            actual = self.test_app.put('/data/0', json=data)
        expected_json = dict(id=0)
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.OK))

    def test_data__update_data__malformed(self):
        data = '{'
        with mock.patch('simple.api.source', self.get_source()):
            actual = self.test_app.put('/data/0', json=data)
        expected_json = dict(data=data)
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.BAD_REQUEST))

    def test_data__update_data__no_data(self):
        data = dict(test='fail')
        with mock.patch('simple.api.source', self.get_source()):
            actual = self.test_app.put('/data/0', json=data)
        expected_json = dict(data=data)
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.BAD_REQUEST))

    def test_data__update_data__not_found(self):
        data = dict(data='gamma')
        with mock.patch('simple.api.source', self.get_source()):
            actual = self.test_app.put('/data/2', json=data)
        expected_json = dict(id=2)
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.NOT_FOUND))

    def test_data__delete_data(self):
        with mock.patch('simple.api.source', self.get_source()):
            actual = self.test_app.delete('/data/0')
        self.assertEqual(
            (actual.data, actual.status_code),
            (b'', HTTPStatus.NO_CONTENT))

    def test_data__delete_data__not_found(self):
        with mock.patch('simple.api.source', self.get_source()):
            actual = self.test_app.delete('/data/2')
        self.assertEqual(
            (actual.data, actual.status_code),
            (b'', HTTPStatus.NOT_FOUND))

    @staticmethod
    def get_source():
        """Source provider."""
        source = util.Source()
        source.add('alpha')
        source.add('beta')
        return source


def main():
    loader = unittest.TestLoader()
    tests = loader.loadTestsFromTestCase(TestSimpleApi)
    unittest.TextTestRunner().run(tests)


if __name__ == "__main__":
    main()
