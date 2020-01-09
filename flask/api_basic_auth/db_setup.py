"""Set up simple SQLite database with credentials table."""
import argparse
import os
import sqlite3

from lib import util

SQL_CREATE_TABLE_USER_CREDENTIALS = """
            CREATE TABLE user_credentials (
              username TEXT PRIMARY KEY,
              password_hash CHAR(64) UNIQUE NOT NULL,
              password_salt CHAR(36) UNIQUE NOT NULL) """


def main(database):
    connection = sqlite3.connect(database)
    with connection:
        connection.execute("DROP TABLE IF EXISTS user_credentials")
    with connection:
        connection.execute(SQL_CREATE_TABLE_USER_CREDENTIALS)
    connection.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Set up SQLite database for Flask REST API.")
    parser.add_argument(
        '--database',
        default=os.path.join(util.DATA_DIR, util.DEFAULT_DATABASE),
        metavar='FILE',
        help='path to database file (default: %(default)s)')
    args = parser.parse_args()
    main(args.database)
