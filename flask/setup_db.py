"""Set up simple SQLite database with sample data."""

import requests

import os
import sqlite3

from lib import util

URL_API_USERS = 'https://jsonplaceholder.typicode.com/users'


def download(url):
    """Download JSON data from API."""
    response = requests.get(url)
    if response.status_code != 200:
        response.raise_for_status()
    return response.json()


def main():
    data = download(URL_API_USERS)
    connection = sqlite3.connect(os.path.join(util.DATA_DIR, util.DEFAULT_DATABASE))
    with connection:
        connection.execute("DROP TABLE IF EXISTS user_data")
    with connection:
        connection.execute(util.SQL_CREATE_TABLE_USER_DATA)
    values = [(user_data['name'], user_data['username'], user_data['email']) for user_data in data]
    with connection:
        connection.executemany(
            "INSERT INTO user_data (name, username, email) VALUES (?, ?, ?)",
            values)
    connection.close()


if __name__ == '__main__':
    main()
