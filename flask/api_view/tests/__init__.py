from flask import Flask
from requests.auth import _basic_auth_str

import os
import unittest

from api_view import api
from api_view import setup_db
from lib import util


# base classes
class BaseApiTestCase(unittest.TestCase):
    """API test case parent class."""
    test_api = None
    test_app = None

    def setUp(self):
        app = Flask('test')
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.test_api = api.ApiServer(app)
        self.test_app = app.test_client()

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
    test_connection = None
    test_source = None

    def setUp(self):
        super(BaseApiTestCaseWithDB, self).setUp()

        # set up database
        connection = util.get_connection(os.path.join(util.DATA_DIR, 'test.sqlite'))
        with connection:
            connection.execute(setup_db.SQL_DROP_TABLE_USERS)
        with connection:
            connection.execute(setup_db.SQL_CREATE_TABLE_USERS)
        util.insert_user(connection, 'one', 'test1', email='test1@example.com', password='pw1')
        util.insert_user(connection, 'two', 'test2', email='test2@example.com', password='pw2')
        self.test_connection = connection
        self.test_source = util.AdminSource(os.path.join(util.DATA_DIR, 'test.sqlite'))


def run():
    tests = unittest.TestLoader().discover(os.path.dirname(__file__))
    suite = unittest.TestSuite(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)
