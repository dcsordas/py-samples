"""Basic REST API using module level functions."""
import sqlite3

from flask import Flask
from flask import jsonify
from flask import request

PORT = 8000

# TODO fix error handling for the entire API
app = Flask(__name__)
source = None


@app.route('/', methods=['HEAD'])
def root():
    return '', 204


@app.route('/data', methods=('GET',))
def get_ids():
    body = dict(ids=sorted(source.get_ids()))
    return jsonify(body), 200


@app.route('/data/<int:id>', methods=('GET',))
def get_data(id):
    body = dict(id=id)
    data = source.get_data(id)
    if data is not None:
        body['data'] = data
        return jsonify(body), 200

    # not found
    return jsonify(body), 404


@app.route('/data', methods=('POST',))
def create_data():
    json = request.get_json()
    try:
        data = json['data']
    except (KeyError, TypeError):
        return jsonify(json), 400

    # process request
    if data:
        id = source.add_data(name=data.get('name'), username=data.get('username'), email=data.get('email'))
        if id is not None:
            return jsonify(dict(id=id)), 201
    return jsonify(json), 400


@app.route('/data/<int:id>', methods=['PUT'])
def update_data(id):
    json = request.get_json()
    try:
        data = json['data']
    except (KeyError, TypeError):
        print('e')
        return jsonify(json), 400

    # process valid request
    if not data:
        return jsonify(json), 400
    if 1 == source.update_data(
            id=id, name=data.get('name'), username=data.get('username'), email=data.get('email')):
        return jsonify(dict(id=id)), 200

    # not found
    return jsonify(data=data), 404


@app.route('/data/<int:id>', methods=['DELETE'])
def delete_data(id):
    try:
        source.delete_data(id)
    except sqlite3.Error:
        return '', 404
    return '', 204
