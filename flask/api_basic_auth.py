"""Basic HTTP authentication."""
import argparse

from flask import Flask
from flask import g
from flask import jsonify
from flask import request
from flask_httpauth import HTTPBasicAuth

from lib import util

PORT = 8001

app = Flask(__name__)
auth = HTTPBasicAuth()
source = util.CredentialsSource()


@auth.verify_password
def verify_password(username, password):
    hash_code = source.get_password_hash(username)
    if not hash_code or hash_code != util.hash_password(password):
        return False
    g.user = username
    return True


# end points
@app.route('/', methods=['HEAD'])
def root():
    return '', 204


@app.route('/users', methods=['GET'])
@auth.login_required
def list_users():
    body = dict(usernames=sorted(source.get_usernames()))
    return jsonify(body), 200


@app.route('/users', methods=['POST'])
def register_user():
    try:
        username = request.form['username']
        password = request.form['password']
    except KeyError:
        body = request.form
        return jsonify(body), 422
    else:
        source.set_credentials(username, util.hash_password(password))
        return '', 201


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Flask REST API.")
    parser.add_argument(
        '--host',
        default='localhost',
        help='server host (default: %(default)s)')
    parser.add_argument(
        '--port',
        default=PORT,
        help='server port (default: %(default)s)')
    args = parser.parse_args()

    # run server
    app.run(host=args.host, port=args.port)
