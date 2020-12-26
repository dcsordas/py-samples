from flask.views import MethodView

import sqlite3
import threading

DATA_DIR = 'data'
DATA_USERS = 'user_data.csv'
DATA_RESOURCES = 'computers.csv'
DEFAULT_DATABASE = 'database.sqlite3'


# TODO drop downloading from API


def get_connection(database):
    """
    Return SQLite connection object.

    :param database: URI to database instance
    :return: connection object
    """
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    return connection


class DatabaseError(sqlite3.Error):
    """Database error exception."""


class Source(object):
    """Parent class for data access objects."""
    _connection = None
    _lock = None

    def __init__(self, connection):
        self._connection = connection
        self._lock = threading.Lock()

    def __del__(self):
        self._connection.close()

    @staticmethod
    def row_to_dict(row, filter_id=True):
        return {key: row[key] for key in row.keys() if not (filter_id and key == 'id')}


class DataSource(Source):
    """SQLite data access object for 'user_data' table."""

    def get_user_ids(self):
        with self._connection:
            cursor = self._connection.execute("SELECT id FROM users")
        rs = cursor.fetchall()
        return [row['id'] for row in rs]

    def get_user(self, id):
        with self._connection:
            cursor = self._connection.execute("SELECT * FROM users WHERE id = ?", (id,))
        row = cursor.fetchone()
        if row:
            return self.row_to_dict(row)

    def add_user(self, name, username, email):
        with self._lock:
            try:
                with self._connection:
                    cursor = self._connection.execute(
                        "INSERT INTO users (name, username, email) VALUES (?, ?, ?)",
                        (name, username, email))
                return cursor.lastrowid
            except sqlite3.Error as error:
                raise DatabaseError(error)

    def update_user(self, id, name, username, email):
        with self._lock:
            try:
                with self._connection:
                    cursor = self._connection.execute(
                        """
                        UPDATE users
                        SET name = ?,
                            username = ?,
                            email = ?
                        WHERE id = ? """,
                        (name, username, email, id))
            except sqlite3.IntegrityError as error:
                raise DatabaseError(error)
            if cursor.rowcount != 1:
                raise DatabaseError('UPDATE failed')

    def delete_user(self, id):
        with self._lock:
            changes = self._connection.total_changes
            with self._connection:
                self._connection.execute("DELETE FROM users WHERE id = ?", (id,))
            if self._connection.total_changes - changes != 1:
                raise DatabaseError('DELETE failed')


class CredentialsSource(Source):
    """SQLite data access object for 'user_credentials' table."""

    def has_username(self, username):
        with self._connection:
            cursor = self._connection.execute("""
                SELECT EXISTS (
                  SELECT 1
                  FROM user_credentials
                  WHERE username = ? ) """, (username,))
        row = cursor.fetchone()
        return bool(row[0])

    def get_usernames(self):
        with self._connection:
            cursor = self._connection.execute("SELECT username FROM user_credentials")
        rs = cursor.fetchall()
        return [row['username'] for row in rs]

    def get_authentication_data(self, username):
        with self._connection:
            cursor = self._connection.execute("""
                SELECT password_hash,
                       password_salt
                FROM user_credentials
                WHERE username = ? """, (username, ))
        row = cursor.fetchone()
        return self.row_to_dict(row)

    def set_credentials(self, username, password_hash, salt):
        with self._lock:
            try:
                with self._connection:
                    cursor = self._connection.execute("""
                        INSERT INTO user_credentials (
                          username,
                          password_hash,
                          password_salt)
                        VALUES (?, ?, ?) """, (username, password_hash, salt))
                return cursor.lastrowid
            except sqlite3.Error as error:
                raise DatabaseError(error)


class SourceView(MethodView):
    """Parent class for MethodView objects handling data source and data extraction."""
    source = None

    def __init__(self, source):
        self.source = source
