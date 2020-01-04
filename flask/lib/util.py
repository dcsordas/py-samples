import sqlite3
import threading

DATA_DIR = 'data'
DEFAULT_DATABASE = 'database.sqlite3'


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


class CredentialsSource(Source):
    """SQLite data access object for 'user_credentials' table."""

    def has_username(self, username):
        with self._connection:
            cursor = self._connection.execute("""
                SELECT EXISTS (
                  SELECT 1
                  FROM user_credentials
                  WHERE username = ? )
            """, (username,))
        row = cursor.fetchone()
        return row[0]

    def get_usernames(self):
        with self._connection:
            cursor = self._connection.execute("SELECT username FROM user_credentials")
        rs = cursor.fetchall()
        return [row['username'] for row in rs]

    def get_authentication_data(self, username):
        # TODO add salt here as well
        with self._connection:
            cursor = self._connection.execute("""
                SELECT password_hash
                FROM user_credentials
                WHERE username = ? """, (username, ))
        row = cursor.fetchone()
        if row:
            return row['password_hash']

    def set_credentials(self, username, password_hash):
        with self._lock:
            with self._connection:
                cursor = self._connection.execute(
                    "INSERT INTO user_credentials (username, password_hash) VALUES (?, ?)",
                    (username, password_hash))
            return cursor.lastrowid
