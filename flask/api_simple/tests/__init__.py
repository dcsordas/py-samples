from requests.auth import _basic_auth_str

import os
import unittest

from api_simple import api
from lib import util


# base classes
class BaseApiTestCase(unittest.TestCase):
    """API test case parent class."""
    test_app = None

    @classmethod
    def setUpClass(cls):
        api.app.testing = True
        api.app.debug = False

    def setUp(self):
        self.test_app = api.app.test_client()

    def get_authorised(self, path, data=None, username='test1', password='pw1'):
        return self.test_app.get(path, data=data, headers={"Authorization": _basic_auth_str(username, password)})

    def delete_authorised(self, path, username='test1', password='pw1'):
        return self.test_app.delete(path, headers={"Authorization": _basic_auth_str(username, password)})

    def post_authorised(self, path, data=None, username='test1', password='pw1'):
        return self.test_app.post(path, data=data, headers={"Authorization": _basic_auth_str(username, password)})

    def put_authorised(self, path, data=None, username='test1', password='pw1'):
        return self.test_app.put(path, data=data, headers={"Authorization": _basic_auth_str(username, password)})


class BaseApiTestCaseWithDB(BaseApiTestCase):
    """API test case parent class with in-memory database fixture."""
    test_source = None

    def setUp(self):
        super(BaseApiTestCaseWithDB, self).setUp()

        # set up database
        dns = util.build_dns(dbname='test')
        with util.connection(dns) as connection:
            with connection.cursor() as cursor:
                cursor.execute("""TRUNCATE TABLE users;""")
                cursor.execute("""ALTER SEQUENCE users_id_seq RESTART WITH 1;""")
            util.insert_user(connection, 'one', 'test1', email='test1@example.com', password='pw1')
            util.insert_user(connection, 'two', 'test2', email='test2@example.com', password='pw2')
        self.test_source = util.AdminSource(dns)


def run():
    tests = unittest.TestLoader().discover(os.path.dirname(__file__))
    suite = unittest.TestSuite(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
