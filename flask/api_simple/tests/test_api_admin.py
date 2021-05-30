from http import HTTPStatus
from unittest import mock

from api_simple.tests import BaseApiTestCaseWithDB


class TestApiAdmin(BaseApiTestCaseWithDB):
    """API /admin end point responses."""

    def test_users_GET__ok(self):
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.get_authorised('/admin/users')
        self.assertEqual(
            (actual.json, actual.status_code),
            (dict(data=['test1', 'test2']), HTTPStatus.OK)
        )

    def test_users_GET__unauthenticated(self):
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.test_app.get('/admin/users')
        self.assertEqual(
            (actual.json, actual.status_code),
            (None, HTTPStatus.UNAUTHORIZED)
        )

    def test_users_GET__unauthorized(self):
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.get_authorised('/admin/users', username='not_a_user', password='not_a_password')
        self.assertEqual(
            (actual.json, actual.status_code),
            (None, HTTPStatus.UNAUTHORIZED)
        )

    def test_users_POST__ok(self):
        data = dict(
            name='new',
            username='test_user',
            email='new@example.com',
            password='test_password'
        )
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.post_authorised('/admin/users', data=data)
        self.assertEqual(
            (actual.json, actual.status_code, self.test_source.has_username(data['username'])),
            (dict(data=dict(id=3)), HTTPStatus.CREATED, True)
        )

    def test_users_POST__unauthenticated(self):
        data = dict(
            name='new',
            username='test_user',
            email='new@example.com',
            password='test_password'
        )
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.test_app.post('/admin/users', data=data)
        self.assertEqual(
            (actual.json, actual.status_code, self.test_source.has_username(data['username'])),
            (None, HTTPStatus.UNAUTHORIZED, False)
        )

    def test_users_POST__unauthorized(self):
        data = dict(
            name='new',
            username='test_user',
            email='new@example.com',
            password='test_password'
        )
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.post_authorised('/admin/users', data=data, username='not_a_user', password='not_a_password')
        self.assertEqual(
            (actual.json, actual.status_code, self.test_source.has_username(data['username'])),
            (None, HTTPStatus.UNAUTHORIZED, False)
        )

    def test_users_POST__duplicate_username(self):
        data = dict(
            name='duplicate',
            username='test1',
            email='duplicate@example.com',
            password='test_password'
        )
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.post_authorised('/admin/users', data=data)
        self.assertEqual(
            (actual.json, actual.status_code, self.test_source.has_username(data['username'])),
            (dict(error='error registering user'), HTTPStatus.INTERNAL_SERVER_ERROR, True)
        )

    def test_users_POST__missing_username(self):
        data = dict(
            name='missing',
            password='test_password',
            email='missing@example.com'
        )
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.post_authorised('/admin/users', data=data)
        self.assertEqual(
            (actual.json, actual.status_code),
            (data, HTTPStatus.UNPROCESSABLE_ENTITY))

    def test_users_POST__missing_password(self):
        data = dict(
            name='missing',
            username='test_user',
            email='missing@example.com'
        )
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.post_authorised('/admin/users', data=data)
        self.assertEqual(
            (actual.json, actual.status_code, self.test_source.has_username(data['username'])),
            (data, HTTPStatus.UNPROCESSABLE_ENTITY, False))

    def test_users_PUT__ok(self):
        data = dict(
            name='neo',
            username='1test',
            email='test1@example.org'
        )
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.put_authorised('/admin/users/1', data=data)
        self.assertEqual(
            (actual.json, actual.status_code, self.test_source.has_username(data['username'])),
            (None, HTTPStatus.NO_CONTENT, True))

    def test_users_PUT__unauthenticated(self):
        data = dict(
            name='neo',
            username='1test',
            email='test1@example.org'
        )
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.test_app.put('/admin/users/1', data=data)
        self.assertEqual(
            (actual.json, actual.status_code, self.test_source.has_username(data['username'])),
            (None, HTTPStatus.UNAUTHORIZED, False))

    def test_users_PUT__unauthorized(self):
        data = dict(
            name='neo',
            username='1test',
            email='test1@example.org'
        )
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.put_authorised('/admin/users/1', data=data, username='not_a_user', password='not_a_password')
        self.assertEqual(
            (actual.json, actual.status_code, self.test_source.has_username(data['username'])),
            (None, HTTPStatus.UNAUTHORIZED, False))

    def test_users_PUT__no_data(self):
        data = None
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.put_authorised('/admin/users/1', data=data)
        expected_json = dict(error='bad/no data in request')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.BAD_REQUEST)
        )
        data = dict()
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.put_authorised('/admin/users/1', data=data)
        expected_json = dict(error='bad/no data in request')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.BAD_REQUEST)
        )

    def test_users_PUT__partial_data(self):
        data = dict(username='success')
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.put_authorised('/admin/users/1', data=data)
        self.assertEqual(
            (actual.json, actual.status_code, self.test_source.has_username('success')),
            (None, HTTPStatus.NO_CONTENT, True)
        )

    def test_users_PUT__not_found(self):
        data = dict(
            name='three',
            username='test3',
            email='test3@example.com'
        )
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.put_authorised('/admin/users/3', data=data)
        expected_json = dict(error='data not updated')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.INTERNAL_SERVER_ERROR)
        )

    def test_users_DELETE__ok(self):
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.delete_authorised('/admin/users/1')
        self.assertEqual(
            (actual.json, actual.status_code, self.test_source.has_username('test1')),
            (None, HTTPStatus.NO_CONTENT, False)
        )

    def test_users_DELETE__not_found(self):
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.delete_authorised('/admin/users/3')
        expected_json = dict(error='data not deleted')
        self.assertEqual(
            (actual.json, actual.status_code),
            (expected_json, HTTPStatus.INTERNAL_SERVER_ERROR)
        )

    def test_users_DELETE__unauthenticated(self):
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.test_app.delete('/admin/users/1')
        self.assertEqual(
            (actual.json, actual.status_code, self.test_source.has_username('test1')),
            (None, HTTPStatus.UNAUTHORIZED, True)
        )

    def test_users_DELETE__unauthorized(self):
        with mock.patch('api_simple.api.source', self.test_source):
            actual = self.delete_authorised('/admin/users/1', username='not_a_user', password='not_a_password')
        self.assertEqual(
            (actual.json, actual.status_code, self.test_source.has_username('test1')),
            (None, HTTPStatus.UNAUTHORIZED, True)
        )
