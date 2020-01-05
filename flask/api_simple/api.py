"""Basic REST API using module level functions."""
from flask import Flask
from flask import jsonify
from flask import request

import sqlite3

PORT = 8000

app = Flask(__name__)
source = None


def extract_data(request):
    """
    Extract structured JSON content from HTTP request.

    :param request: HTTP request object
    :return: JSON content subset under 'data' key
    """
    json = request.get_json()
    try:
        data = json['data']
    except (KeyError, TypeError):
        raise
    if not data:
        raise ValueError('No data')
    return data


# end points
@app.route('/', methods=['HEAD'])
def root():
    return '', 204


@app.route('/data', methods=('GET',))
def get_ids():
    ids = source.get_ids()
    return jsonify(dict(ids=sorted(ids))), 200


@app.route('/data/<int:id>', methods=('GET',))
def get_data(id):
    data = source.get_data(id)
    if data:
        return jsonify(dict(data=data)), 200

    # not found
    return jsonify(error='Not found'), 404


@app.route('/data', methods=('POST',))
def create_data():
    try:
        data = extract_data(request)
    except Exception as error:
        return jsonify(dict(error=str(error))), 400

    # process request
    try:
        id = source.add_data(name=data.get('name'), username=data.get('username'), email=data.get('email'))
    except sqlite3.Error as error:
        return jsonify(error=str(error)), 500
    else:
        return jsonify(dict(id=id)), 201


@app.route('/data/<int:id>', methods=['PUT'])
def update_data(id):
    try:
        data = extract_data(request)
    except Exception as error:
        return jsonify(dict(error=str(error))), 400

    # process valid request
    try:
        source.update_data(
            id=id, name=data.get('name'), username=data.get('username'), email=data.get('email'))
    except sqlite3.Error as error:
        return jsonify(dict(error=str(error))), 500
    else:
        return '', 204


@app.route('/data/<int:id>', methods=['DELETE'])
def delete_data(id):
    try:
        source.delete_data(id)
    except sqlite3.Error as error:
        return jsonify(dict(error=str(error))), 500
    return '', 204
