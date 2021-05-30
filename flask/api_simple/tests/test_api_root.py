from http import HTTPStatus

from api_simple.tests import BaseApiTestCase


class TestApiRoot(BaseApiTestCase):
    """API root end point responses."""

    def test_HEADER(self):
        actual = self.test_app.head('/')
        self.assertEqual(
            (actual.json, actual.status_code),
            (None, HTTPStatus.NO_CONTENT))
