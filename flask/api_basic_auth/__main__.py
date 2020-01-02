import argparse
import os

from . import api
from lib import util


def main(args):
    api.app.run(host=args.host, port=args.port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Flask REST API (with basic HTTP authentication).")
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
        help='run tests')
    args = parser.parse_args()

    # test
    if args.test:
        from . import test
        test.main()

    # run server
    else:
        main(args)
