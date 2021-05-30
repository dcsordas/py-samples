from http import HTTPStatus

from api_view.tests import BaseApiTestCase
from api_view import api


class TestApiRoot(BaseApiTestCase):
    """API root end point responses."""

    def setUp(self):
        super(TestApiRoot, self).setUp()
        api.RootView.register_view(self.test_api.app, source=None)

    def test_HEADER(self):
        actual = self.test_app.head('/')
        self.assertEqual(
            (actual.json, actual.status_code),
            (None, HTTPStatus.NO_CONTENT))