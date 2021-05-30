"""Basic REST API using module level functions."""
import uuid

from flask import Flask, g, Blueprint
from flask import jsonify
from flask import request
from flask_httpauth import HTTPBasicAuth

from lib import util
from lib.util import hash_password

PORT = 8000

app = Flask(__name__)
source = None


# Root
@app.route('/', methods=['HEAD'])
def root():
    return '', 204


# authentication
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    if source.has_username(username) is True:
        result = source.get_authentication_data(username)
        hash_code = result['password_hash']
        salt = result['password_salt']

        # verify
        if hash_code == hash_password(password, salt):
            g.user = username
            return True
    return False


# Admin API
admin_api = Blueprint('admin', __name__, url_prefix='/admin')


@admin_api.route('/users', methods=['GET'])
@auth.login_required
def list_users():
    data = dict(data=sorted(source.get_usernames()))
    return jsonify(data), 200


@admin_api.route('/users/<int:user_id>', methods=('GET',))
@auth.login_required
def get_user(user_id):
    data = source.get_user(user_id)
    if data:
        return jsonify(dict(data=data)), 200

    # not found
    return jsonify(error='data not found'), 404


@admin_api.route('/users', methods=['POST'])
@auth.login_required
def register_user():
    try:
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
    except KeyError:
        body = request.form
        return jsonify(body), 422
    salt = str(uuid.uuid4())
    password_hash = hash_password(password, salt)
    try:
        user_id = source.add_user(name, username, email, password_hash, salt)
        return jsonify(data=dict(id=user_id)), 201
    except util.DatabaseError:
        return jsonify(error='error registering user'), 500


@admin_api.route('/users/<int:user_id>', methods=['PUT'])
@auth.login_required
def update_user(user_id):
    if not request.form:
        return jsonify(dict(error='bad/no data in request')), 400
    try:
        source.update_user(
            user_id,
            name=request.form.get('name'),
            username=request.form.get('username'),
            email=request.form.get('email'),
            password=request.form.get('password')
        )
    except util.DatabaseError:
        return jsonify(dict(error='data not updated')), 500
    else:
        return '', 204


@admin_api.route('/users/<int:user_id>', methods=['DELETE'])
@auth.login_required
def delete_user(user_id):
    try:
        source.delete_user(user_id)
    except util.DatabaseError:
        return jsonify(dict(error=str('data not deleted'))), 500
    else:
        return '', 204


app.register_blueprint(admin_api)
