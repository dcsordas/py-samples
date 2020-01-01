"""Set up simple SQLite database with sample data."""

import requests

import sqlite3

URL_API_USERS = 'https://jsonplaceholder.typicode.com/users'
URI_DATABASE = 'data/database.sqlite3'


def download(url):
    """Download JSON data from API."""
    response = requests.get(url)
    if response.status_code != 200:
        response.raise_for_status()
    return response.json()


def main():
    data = download(URL_API_USERS)
    connection = sqlite3.connect(URI_DATABASE)
    with connection:
        connection.execute("DROP TABLE IF EXISTS users")
    with connection:
        connection.execute("""
            CREATE TABLE users (
              id INTEGER PRIMARY KEY,
              name TEXT NOT NULL,
              username TEXT NOT NULL,
              email TEXT NOT NULL) """)
    values = [(user['name'], user['username'], user['email']) for user in data]
    with connection:
        connection.executemany(
            "INSERT INTO users (name, username, email) VALUES (?, ?, ?)",
            values)
    connection.close()


if __name__ == '__main__':
    main()
