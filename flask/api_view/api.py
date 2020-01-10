"""Object oriented REST API using View classes."""
from flask import jsonify
from flask import request
from flask.views import MethodView

from lib import util

PORT = 8002


# view classes
class RootView(MethodView):
    """API root view."""

    @classmethod
    def register_view(cls, app, source=None):
        app.add_url_rule('/', view_func=cls.as_view('root'))

    def head(self):
        return '', 204


class DataView(util.SourceView):
    """API data/ end point view."""
    source = None

    @classmethod
    def register_view(cls, app, source):
        data_view = cls.as_view('/data', source=source)
        app.add_url_rule(
            '/data',
            view_func=data_view,
            defaults=dict(data_id=None),
            methods=('GET',))
        app.add_url_rule(
            '/data/<int:data_id>',
            view_func=data_view,
            methods=('GET', 'PUT', 'DELETE'))
        app.add_url_rule(
            '/data',
            view_func=data_view,
            methods=('POST',))

    def get(self, data_id):
        if data_id is None:

            # list ids
            data_ids = self.source.get_ids()
            return jsonify(dict(ids=sorted(data_ids))), 200
        else:

            # get data
            data = self.source.get_data(data_id)
            if data:
                return jsonify(dict(data=data)), 200

            # not found
            return jsonify(error='data not found'), 404

    def post(self):
        try:
            data = util.extract_data(request)
        except ValueError as error:
            return jsonify(dict(error=str(error))), 400

        # process request
        try:
            data_id = self.source.add_data(name=data.get('name'), username=data.get('username'), email=data.get('email'))
        except util.DatabaseError:
            return jsonify(error='data not created'), 500
        else:
            return jsonify(dict(id=data_id)), 201

    def put(self, data_id):
        try:
            data = util.extract_data(request)
        except ValueError as error:
            return jsonify(dict(error=str(error))), 400

        # process valid request
        try:
            self.source.update_data(
                id=data_id, name=data.get('name'), username=data.get('username'), email=data.get('email'))
        except util.DatabaseError:
            return jsonify(dict(error='data not updated')), 500
        else:
            return '', 204

    def delete(self, data_id):
        try:
            self.source.delete_data(data_id)
        except util.DatabaseError:
            return jsonify(dict(error='data not deleted')), 500
        else:
            return '', 204


# Flask application wrapper
class ApiServer(object):
    app = None
    views = (RootView, DataView)

    def __init__(self, app):
        self.app = app

    def run(self, host, port):
        """
        Run server.

        :param host: server host
        :param port: server port
        """
        self.app.run(host, port)
