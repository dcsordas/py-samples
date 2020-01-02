from hashlib import sha1
import pprint
import sqlite3
import threading

DATA_DIR = 'data'
DEFAULT_DATABASE = 'database.sqlite3'

SQL_CREATE_TABLE_USER_DATA = """
            CREATE TABLE user_data (
              id INTEGER PRIMARY KEY,
              name TEXT NOT NULL,
              username TEXT UNIQUE NOT NULL,
              email TEXT UNIQUE NOT NULL) """


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
        raise
    if not data:
        raise ValueError('No data')
    return data


def hash_password(password):
    """
    Return SHA1 hash for input.

    :param password: password string
    :return: password hash code
    """
    return sha1(password.encode()).hexdigest()


def get_connection(database):
    """
    Return SQLite connection object.

    :param database: URI to database instance
    :return: connection object
    """
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    return connection


class Source(object):
    """Parent class for data access objects."""
    _connection = None
    _lock = None

    def __init__(self, connection):
        self._connection = connection
        self._lock = threading.Lock()

    def __del__(self):
        self._connection.close()


class DataSource(Source):
    """SQLite data access object for 'user_data' table."""

    @staticmethod
    def row_to_dict(row, filter_id=True):
        return {key: row[key] for key in row.keys() if not (filter_id and key == 'id')}

    def get_ids(self):
        with self._connection:
            cursor = self._connection.execute("SELECT id FROM user_data")
        rs = cursor.fetchall()
        return [row['id'] for row in rs]

    def get_data(self, id):
        with self._connection:
            cursor = self._connection.execute("SELECT * FROM user_data WHERE id = ?", (id,))
        row = cursor.fetchone()
        if row:
            return self.row_to_dict(row)

    def add_data(self, name, username, email):
        with self._lock:
            with self._connection:
                cursor = self._connection.execute(
                    "INSERT INTO user_data (name, username, email) VALUES (?, ?, ?)",
                    (name, username, email))
            return cursor.lastrowid

    def update_data(self, id, name, username, email):
        with self._lock:
            with self._connection:
                cursor = self._connection.execute(
                    """
                    UPDATE user_data
                    SET name = ?,
                        username = ?,
                        email = ?
                    WHERE id = ? """,
                    (name, username, email, id))
            if cursor.rowcount != 1:
                raise sqlite3.Error('UPDATE failed')

    def delete_data(self, id):
        with self._lock:
            changes = self._connection.total_changes
            with self._connection:
                self._connection.execute("DELETE FROM user_data WHERE id = ?", (id,))
            if self._connection.total_changes - changes != 1:
                raise sqlite3.Error('DELETE failed')


class CredentialsSource(object):
    storage = None
    lock = None

    def __init__(self):
        self.storage = {}
        self.lock = threading.Lock()

    def __str__(self):
        return pprint.pformat(self.storage)

    def has_username(self, username):
        """Return if username was found in storage."""
        return username in self.storage

    def get_usernames(self):
        """Return list of registered usernames."""
        return self.storage.keys()

    def get_password_hash(self, username):
        """Return password hash if found (or None)."""
        return self.storage.get(username)

    def set_credentials(self, username, password_hash):
        """Create or update credentials in database."""
        with self.lock:
            self.storage[username] = password_hash
