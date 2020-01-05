"""Set up simple SQLite database with sample data."""
import requests

import argparse
import os
import sqlite3

from lib import util

SQL_CREATE_TABLE_USER_DATA = """
            CREATE TABLE user_data (
              id INTEGER PRIMARY KEY,
              name TEXT NOT NULL,
              username TEXT UNIQUE NOT NULL,
              email TEXT UNIQUE NOT NULL) """

URL_API_USERS = 'https://jsonplaceholder.typicode.com/users'


def download(url):
    """Download JSON data from API."""
    response = requests.get(url)
    if response.status_code != 200:
        response.raise_for_status()
    return response.json()


def main(database, data_from_url):
    connection = sqlite3.connect(database)
    with connection:
        connection.execute("DROP TABLE IF EXISTS user_data")
    with connection:
        connection.execute(SQL_CREATE_TABLE_USER_DATA)

    # add predefined data
    if data_from_url:
        data = download(URL_API_USERS)
        values = [(user_data['name'], user_data['username'], user_data['email']) for user_data in data]
        with connection:
            connection.executemany(
                "INSERT INTO user_data (name, username, email) VALUES (?, ?, ?)",
                values)
        connection.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Set up SQLite database for Flask REST API.")
    parser.add_argument(
        '--database',
        default=os.path.join(util.DATA_DIR, util.DEFAULT_DATABASE),
        metavar='FILE',
        help='path to database file (default: %(default)s)')
    parser.add_argument(
        '--data-from-url',
        default=False,
        action='store_true',
        help='add data downloaded from %s (default: %%(default)s)' % URL_API_USERS)
    args = parser.parse_args()
    main(args.database, args.data_from_url)
