import argparse
import os

from . import api
from lib import util


def main(host, port, database):
    connection = util.get_connection(database)
    api.source = util.DataSource(connection)
    api.app.run(host=host, port=port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Flask REST API (with api_simple module level end points).")
    parser.add_argument(
        '--host',
        default='localhost',
        help='server host (default: %(default)s)')
    parser.add_argument(
        '--port',
        default=api.PORT,
        help='server port (default: %(default)s)')
    parser.add_argument(
        '--test',
        action='store_true',
        default=False,
        help='run tests and exit')

    parser.add_argument(
        '--database',
        default=os.path.join(util.DATA_DIR, util.DEFAULT_DATABASE),
        metavar='FILE',
        help='path to database file (default: %(default)s)')
    args = parser.parse_args()

    # run tests
    if args.test:
        from . import tests
        tests.run()

    # run server
    else:
        main(args.host, args.port, args.database)
