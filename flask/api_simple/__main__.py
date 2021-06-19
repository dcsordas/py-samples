import argparse

from . import api
from lib import util


def main(host, port):
    api.source = util.AdminSource(util.build_dns())
    api.app.run(host=host, port=port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Flask REST API (with api_simple module level end points).")
    subparsers = parser.add_subparsers(dest='command')
    subparsers.metavar = 'commands'

    # command: run
    cmd_run = subparsers.add_parser(
        'run',
        help='run server',
        description='Run Flask server.')
    cmd_run.add_argument(
        '--host',
        default='localhost',
        help='server host (default: %(default)s)')
    cmd_run.add_argument(
        '--port',
        default=api.PORT,
        help='server port (default: %(default)s)')

    # command: test
    cmd_test = subparsers.add_parser(
        'test',
        help='run tests',
        description='Run unittests.')

    # command: data
    cmd_data = subparsers.add_parser(
        'data',
        help='manage database',
        description='Set up and manage database.')
    cmd_data.add_argument(
        '--data-from-url',
        default=False,
        action='store_true',
        help='insert data downloaded from %s (default: %%(default)s)' % util.URL_JSONPLACEHOLDER_API_USERS)

    # parse and evaluate
    args = parser.parse_args()
    if args.command == 'test':
        from . import tests
        tests.run()
    elif args.command == 'data':
        from . import setup_db
        setup_db.main(args.data_from_url)
    elif args.command == 'run':
        main(args.host, args.port)
    else:
        print('%s: error: argument commands: no command provided\n' % __name__)
        parser.print_help()
        exit(1)
