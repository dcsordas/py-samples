from hashlib import sha1
import json
import pprint
import threading

DATA_DIR = 'data'


def hash_password(password):
    """
    Return SHA1 hash for input.

    :param password: password string
    :return: password hash code
    """
    return sha1(password.encode()).hexdigest()


def load_data(filepath):
    """
    Return JSON from file path.

    :param filepath: path to JSON file
    :return: JSON object
    """
    with open(filepath, 'r') as f:
        return json.load(f)


class Source(object):
    storage = None

    def __init__(self):
        self.storage = {}

    def __str__(self):
        return pprint.pformat(self.storage)

    def keys(self):
        return list(self.storage.keys())

    def get(self, key):
        return self.storage.get(key)

    def add(self, record):
        if self.storage.keys():
            key = max(self.storage.keys()) + 1
        else:
            key = 0
        self.storage[key] = record
        return key

    def update(self, key, record):
        if key in self.storage:
            self.storage[key] = record
            return key

    def delete(self, key):
        if key in self.storage:
            del self.storage[key]
            return key


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
