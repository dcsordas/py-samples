"""Set up simple SQLite database with sample data."""
import argparse
import csv
import os
import sqlite3

from lib import util

SQL_CREATE_TABLE_USER_DATA = """
            CREATE TABLE user_data (
              id INTEGER PRIMARY KEY,
              name TEXT NOT NULL,
              username TEXT UNIQUE NOT NULL,
              email TEXT UNIQUE NOT NULL) """


def main(database, data_from_file, data_from_url):
    connection = sqlite3.connect(database)
    with connection:
        connection.execute("DROP TABLE IF EXISTS user_data")
    with connection:
        connection.execute(SQL_CREATE_TABLE_USER_DATA)

    # insert data to database
    data_source = None
    if data_from_file:
        with open(os.path.join(util.DATA_DIR, util.DATA_FILE)) as f:
            reader = csv.DictReader(f)
            data_source = [user_data for user_data in reader]
    elif data_from_url:
        data_source = util.download_data(util.URL_JSONPLACEHOLDER_API_USERS)
    else:
        exit(0)
    if data_source is not None:
        values = [(user_data['name'], user_data['username'], user_data['email']) for user_data in data_source]
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
        '--data-from-file',
        default=True,
        action='store_false',
        help='insert data loaded from %s (default: %%(default)s)' % os.path.join(util.DATA_DIR, util.DATA_FILE))
    parser.add_argument(
        '--data-from-url',
        default=False,
        action='store_true',
        help='insert data downloaded from %s (default: %%(default)s)' % util.URL_JSONPLACEHOLDER_API_USERS)
    args = parser.parse_args()
    main(args.database, args.data_from_file, args.data_from_url)
