"""Basic REST API using module level functions."""
from flask import Flask
from flask import jsonify
from flask import request

from lib import util

PORT = 8000

app = Flask(__name__)
source = None


# end points
@app.route('/', methods=['HEAD'])
def root():
    return '', 204


@app.route('/data', methods=('GET',))
def get_ids():
    data_ids = source.get_ids()
    return jsonify(dict(ids=sorted(data_ids))), 200


@app.route('/data/<int:data_id>', methods=('GET',))
def get_data(data_id):
    data = source.get_data(data_id)
    if data:
        return jsonify(dict(data=data)), 200

    # not found
    return jsonify(error='data not found'), 404


@app.route('/data', methods=('POST',))
def create_data():
    try:
        data = util.extract_data(request)
    except ValueError as error:
        return jsonify(dict(error=str(error))), 400

    # process request
    try:
        data_id = source.add_data(name=data.get('name'), username=data.get('username'), email=data.get('email'))
    except util.DatabaseError:
        return jsonify(error='data not created'), 500
    else:
        return jsonify(dict(id=data_id)), 201


@app.route('/data/<int:data_id>', methods=['PUT'])
def update_data(data_id):
    try:
        data = util.extract_data(request)
    except ValueError as error:
        return jsonify(dict(error=str(error))), 400

    # process valid request
    try:
        source.update_data(
            id=data_id, name=data.get('name'), username=data.get('username'), email=data.get('email'))
    except util.DatabaseError:
        return jsonify(dict(error='data not updated')), 500
    else:
        return '', 204


@app.route('/data/<int:data_id>', methods=['DELETE'])
def delete_data(data_id):
    try:
        source.delete_data(data_id)
    except util.DatabaseError:
        return jsonify(dict(error=str('data not deleted'))), 500
    else:
        return '', 204
