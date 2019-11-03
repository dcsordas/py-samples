"""Basic REST API using module level functions."""

from flask import Flask
from flask import jsonify
from flask import request

import argparse
import os

from lib import util

PORT = 8000

app = Flask(__name__)
source = util.Source()


@app.route('/', methods=['HEAD'])
def root():
    return '', 204


@app.route('/data', methods=('GET',))
def get_ids():
    body = dict(ids=sorted(source.keys()))
    return jsonify(body), 200


@app.route('/data/<int:id>', methods=('GET',))
def get_data(id):
    body = dict(id=id)
    data = source.get(id)
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
        body = dict(data=json)
        return jsonify(body), 400

    # return response
    id = source.add(data)
    body = dict(id=id)
    return jsonify(body), 201


@app.route('/data/<int:id>', methods=['PUT'])
def update_data(id):
    json = request.get_json()
    try:
        data = json['data']
    except (KeyError, TypeError):
        return jsonify(dict(data=json)), 400

    # process valid request
    body = dict(id=id)
    if id == source.update(id, data):
        return jsonify(body), 200

    # not found
    return jsonify(body), 404


@app.route('/data/<int:id>', methods=['DELETE'])
def delete_data(id):
    if id == source.delete(id):
        return '', 204

    # not found
    return '', 404


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

    parser.add_argument(
        '--data',
        default=os.path.join(util.DATA_DIR, 'input.json'),
        metavar='FILE',
        help='path to JSON data file (default: %(default)s)')
    args = parser.parse_args()

    # set up data
    for record in util.load_data(args.data):
        source.add(record)

    # run server
    app.run(host=args.host, port=args.port)
