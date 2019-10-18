from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)
data = None


@app.route('/', methods=['HEAD'])
def root():
    return '', 204


@app.route('/data', methods=['GET'])
def get_ids():
    ids = sorted(data.keys())
    return jsonify(dict(ids=ids)), 200


@app.route('/data/<path:data_id>', methods=['GET'])
def get_data(data_id):
    value = data.get(data_id)
    status_code = 404 if value is None else 200
    response = {data_id: value}
    return jsonify(response), status_code


@app.route('/data', methods=['POST'])
def create_data():
    load = request.get_json()
    try:
        key = load['id']
        value = load['value']
    except KeyError:
        return jsonify(dict(data=load)), 400
    status_code = 201
    if key not in data:
        data[key] = value
    else:
        status_code = 409
    return jsonify(dict(id=key)), status_code


@app.route('/data/<path:data_id>', methods=['PUT'])
def update_data(data_id):
    load = request.get_json()
    try:
        value = load['value']
    except KeyError:
        return jsonify(dict(data=load)), 400

    # process valid request
    data[data_id] = value
    return jsonify(dict(id=data_id)), 200


@app.route('/data/<path:data_id>', methods=['DELETE'])
def delete_data(data_id):
    status_code = 204
    try:
        del data[data_id]
    except KeyError:
        status_code = 404
    return '', status_code


if __name__ == '__main__':
    data = dict(alpha=1, beta=2, delta=3, gamma=4)
    app.run(host='localhost', port=8000)
