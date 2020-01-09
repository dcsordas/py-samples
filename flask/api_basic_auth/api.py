"""Basic HTTP authentication."""
from flask import Flask
from flask import g
from flask import jsonify
from flask import request
from flask_httpauth import HTTPBasicAuth

from hashlib import sha256
import uuid

PORT = 8001

app = Flask(__name__)
auth = HTTPBasicAuth()
source = None


def hash_password(password, salt):
    """
    Return SHA256 hash for input.

    Note: Does not count as production eligible security measure.

    :param password: password string
    :param salt: salt string
    :return: password hash code
    """
    encoded = (password + salt).encode()
    return sha256(encoded).hexdigest()


@auth.verify_password
def verify_password(username, password):
    try:
        hash_code, salt = source.get_authentication_data(username)
    except:
        return False

    # verify
    if hash_code != hash_password(password, salt):
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
        salt = str(uuid.uuid4())
        password_hash = hash_password(password, salt)
        source.set_credentials(username, password_hash, salt)
        return '', 201
