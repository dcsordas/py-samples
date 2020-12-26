"""Set up simple SQLite database with sample data."""
import argparse
import csv
import os
import sqlite3

from lib import util

# SQL_CREATE_TABLES = {
#     'users': """
#             CREATE TABLE users (
#               id INTEGER PRIMARY KEY,
#               name TEXT NOT NULL,
#               username TEXT UNIQUE NOT NULL,
#               email TEXT UNIQUE NOT NULL);""",
#     'resources': """
#             CREATE TABLE resources (
#               id INTEGER PRIMARY KEY,
#               name TEXT UNIQUE NOT NULL,
#               type TEXT NOT NULL);""",
#     'users_resources': """
#             CREATE TABLE users_resources (
#               id INTEGER PRIMARY KEY,
#               user_id INTEGER NOT NULL,
#               resource_id INTEGER NOT NULL,
#               FOREIGN KEY (user_id) REFERENCES users (id),
#               FOREIGN KEY (resource_id) REFERENCES resources (id),
#               UNIQUE (user_id, resource_id));"""
# }


def main(database):
    connection = sqlite3.connect(database)
    with open(os.path.join(util.DATA_DIR, 'schema.sql')) as schema_file:
        schema_script = schema_file.read()

    with connection:
        connection.executescript(schema_script)
    print('... created schema')

    # insert table rows
    csv_dir = os.path.join(util.DATA_DIR, 'csv')
    files = [
        f
        for f
        in os.listdir(csv_dir)
        if os.path.isfile(os.path.join(csv_dir, f)) and f.endswith('.csv')
    ]
    for fn in files:
        with open(os.path.join(csv_dir, fn)) as csv_file:
            reader = csv.DictReader(csv_file)
            rows = [row for row in reader]
        table = fn.split('.')[0]
        columns = reader.fieldnames
        query = "INSERT INTO {table} ({columns}) VALUES ({values})".format(
            table=table,
            columns=', '.join(columns),
            values=', '.join(['?'] * len(columns))
        )
        with connection:
            connection.executemany(
                query,
                ([row[column] for column in columns] for row in rows)
            )
        print('... populated table: {}'.format(table))

    # TODO populate users_resources
    relations = 3
    user_resource_mappings = {}
    resource_user_mappings = {}
    with connection:
        user_ids = [row[0] for row in connection.execute("SELECT id FROM users ORDER BY id;")]
        resource_ids = [row[0] for row in connection.execute("SELECT id FROM resources ORDER BY id;")]
    print(user_ids)
    print(resource_ids)

    connection.close()




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Set up SQLite database for Flask REST API.")
    parser.add_argument(
        '--database',
        default=os.path.join(util.DATA_DIR, util.DEFAULT_DATABASE),
        metavar='FILE',
        help='path to database file (default: %(default)s)')
    # parser.add_argument(
    #     '--data-from-file',
    #     default=True,
    #     action='store_false',
    #     help='insert data loaded from %s (default: %%(default)s)' % os.path.join(util.DATA_DIR, util.DATA_FILE))
    args = parser.parse_args()
    main(args.database)
