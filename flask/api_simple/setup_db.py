"""Set up simple SQLite database with sample data."""
import argparse
import os
import sqlite3

from lib import util

SQL_CREATE_TABLE_USERS = """
            CREATE TABLE users (
              id INTEGER PRIMARY KEY,
              name TEXT NOT NULL,
              username TEXT UNIQUE NOT NULL,
              email TEXT UNIQUE NOT NULL,
              password_hash CHAR(64) UNIQUE NOT NULL,
              password_salt CHAR(36) UNIQUE NOT NULL) """
SQL_DROP_TABLE_USERS = "DROP TABLE IF EXISTS users;"


def main(database, data_from_url):
    connection = sqlite3.connect(database)
    with connection:
        connection.execute(SQL_DROP_TABLE_USERS)
    with connection:
        connection.execute(SQL_CREATE_TABLE_USERS)

    # insert data to database
    util.insert_user(connection, 'admin', 'admin', password='admin')
    if data_from_url:
        data_source = util.download_data(util.URL_JSONPLACEHOLDER_API_USERS)
        for user_data in data_source:
            util.insert_user(connection, user_data['name'], user_data['username'], email=user_data['email'])
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
        help='insert data downloaded from %s (default: %%(default)s)' % util.URL_JSONPLACEHOLDER_API_USERS)
    args = parser.parse_args()
    main(args.database, args.data_from_url)
