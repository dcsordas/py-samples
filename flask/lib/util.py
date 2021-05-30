from hashlib import sha256
import threading
import uuid

from flask import g
from flask.views import MethodView
import requests

import sqlite3

from flask_httpauth import HTTPBasicAuth

DATA_DIR = 'data'
DEFAULT_DATABASE = 'database.sqlite3'
TEST_DATABASE = 'test.sqlite3'
URL_JSONPLACEHOLDER_API_USERS = 'https://jsonplaceholder.typicode.com/users'


def download_data(url):
    """Download JSON data from API."""
    response = requests.get(url)
    if response.status_code != 200:
        response.raise_for_status()
    return response.json()


def extract_data(request):
    """
    Extract structured JSON content from HTTP request.

    :param request: HTTP request object
    :return: JSON content subset under 'data' key
    """
    json = request.get_json()
    try:
        data = json['data']
    except (KeyError, TypeError):
        raise ValueError('bad/no data in request')
    else:
        if not data:
            raise ValueError('bad/no data in request')
    return data


def get_connection(database):
    """
    Return SQLite connection object.

    :param database: URI to database instance
    :return: connection object
    """
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    return connection


def insert_user(connection, name, username, email=None, password=None):
    email = email or '{}@example.com'.format(username)
    password_salt = str(uuid.uuid4())
    password_hash = hash_password(password or username, password_salt)
    with connection:
        connection.execute(
            "INSERT INTO users (name, username, email, password_salt, password_hash) VALUES (?, ?, ?, ?, ?)",
            (name, username, email, password_salt, password_hash)
        )


def hash_password(password, salt):
    """
    Return SHA256 hash for input.

    Note: Does not count as production eligible security measure.

    :param password: password string
    :param salt: salt string
    :return: password hash code
    """
    encoded = (password + salt).encode()
    return sha256(encoded).hexdigest()


class DatabaseError(sqlite3.Error):
    """Database error exception."""


class Source(object):
    """Parent class for data access objects."""
    _database = None
    _lock = None

    def __init__(self, database):
        self._database = database
        self._lock = threading.Lock()

    def get_connection(self):
        return get_connection(self._database)

    @staticmethod
    def row_to_dict(row, filter_id=True):
        return {key: row[key] for key in row.keys() if not (filter_id and key == 'id')}


class AdminSource(Source):
    """SQLite data access object for 'users' table."""

    def get_ids(self):
        with self.get_connection() as connection:
            cursor = connection.execute("SELECT id FROM users")
        rs = cursor.fetchall()
        return [row['id'] for row in rs]

    def get_user(self, user_id):
        with self.get_connection() as connection:
            cursor = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return self.row_to_dict(row)

    def add_user(self, name, username, email, password_hash, password_salt):
        with self._lock:
            try:
                with self.get_connection() as connection:
                    cursor = connection.execute(
                        """
                        INSERT INTO users (name, username, email, password_hash, password_salt)
                            VALUES (?, ?, ?, ?, ?)
                        """,
                        (name, username, email, password_hash, password_salt))
                return cursor.lastrowid
            except sqlite3.Error as error:
                raise DatabaseError(error)

    def update_user(self, user_id, **kwargs):
        query = """
                    UPDATE users
                    SET {block}
                    WHERE id = ? """
        values = []
        block_parts = []
        for name, value in kwargs.items():
            if value:
                if name == 'password':
                    password_salt = str(uuid.uuid4())
                    password_hash = hash_password(value, password_salt)
                    block_parts.extend(['password_salt = ?', 'password_hash = ?'])
                    values.extend([password_salt, password_hash])
                else:
                    block_parts.append('{} = ?'.format(name))
                    values.append(value)
        values.append(user_id)
        with self._lock:
            try:
                with self.get_connection() as connection:
                    cursor = connection.execute(
                        query.format(block=', '.join(block_parts)),
                        values
                    )
            except sqlite3.IntegrityError as error:
                raise DatabaseError(error)
            if cursor.rowcount != 1:
                raise DatabaseError('UPDATE failed')

    def delete_user(self, user_id):
        with self._lock:
            connection = self.get_connection()
            changes = connection.total_changes
            with connection:
                connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
            if connection.total_changes - changes != 1:
                raise DatabaseError('DELETE failed')

    def has_username(self, username):
        with self._lock:
            with self.get_connection() as connection:
                cursor = connection.execute("""
                    SELECT EXISTS (
                      SELECT 1
                      FROM users
                      WHERE username = ? ) """, (username,))
            row = cursor.fetchone()
            return bool(row[0])

    def get_usernames(self):
        with self.get_connection() as connection:
            cursor = connection.execute("SELECT username FROM users")
        rs = cursor.fetchall()
        return [row['username'] for row in rs]

    def get_authentication_data(self, username):
        with self.get_connection() as connection:
            cursor = connection.execute("""
                SELECT password_hash,
                       password_salt
                FROM users
                WHERE username = ? """, (username, ))
        row = cursor.fetchone()
        return self.row_to_dict(row)


def get_verify_password(source):
    """Factory function to provide verify_password closures with access to DB source for HTTPBasicAuth instances."""

    def verify_password(username, password):
        if source.has_username(username) is True:
            result = source.get_authentication_data(username)
            hash_code = result['password_hash']
            salt = result['password_salt']

            # verify
            if hash_code == hash_password(password, salt):
                g.user = username
                return True
        return False
    return verify_password


class SourceView(MethodView):
    """Parent class for MethodView objects handling data source and data extraction."""
    decorators = []
    source = None

    def __init__(self, source):
        self.source = source
        auth = HTTPBasicAuth()
        auth.verify_password(get_verify_password(source))
        self.decorators.append(auth.login_required)
