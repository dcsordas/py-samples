"""Set up simple SQLite database with sample data."""
import argparse

from lib import util


def main(data_from_url):
    with util.connection() as connection:

        # insert data to database
        util.insert_user(connection, 'admin', 'admin', password='admin')
        if data_from_url:
            data_source = util.download_data(util.URL_JSONPLACEHOLDER_API_USERS)
            for user_data in data_source:
                util.insert_user(connection, user_data['name'], user_data['username'], email=user_data['email'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Set up SQLite database for Flask REST API.")
    parser.add_argument(
        '--data-from-url',
        default=False,
        action='store_true',
        help='insert data downloaded from %s (default: %%(default)s)' % util.URL_JSONPLACEHOLDER_API_USERS)
    args = parser.parse_args()
    main(args.data_from_url)
