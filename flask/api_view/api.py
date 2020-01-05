"""Object oriented REST API using View classes."""
from flask import jsonify
from flask import request
from flask.views import MethodView

import sqlite3

from lib.util import SourceView

PORT = 8002


# view classes
class RootView(MethodView):
    """API root view."""

    @classmethod
    def register_view(cls, app, source=None):
        app.add_url_rule('/', view_func=cls.as_view('root'))

    def head(self):
        return '', 204


class DataView(SourceView):
    """API data/ end point view."""
    source = None

    @classmethod
    def register_view(cls, app, source):
        data_view = cls.as_view('/data', source=source)
        app.add_url_rule(
            '/data',
            view_func=data_view,
            defaults=dict(id=None),
            methods=('GET',))
        app.add_url_rule(
            '/data/<int:id>',
            view_func=data_view,
            methods=('GET', 'PUT', 'DELETE'))
        app.add_url_rule(
            '/data',
            view_func=data_view,
            methods=('POST',))

    def get(self, id):
        if id is None:

            # list ids
            ids = self.source.get_ids()
            return jsonify(dict(ids=sorted(ids))), 200
        else:

            # get data
            data = self.source.get_data(id)
            if data:
                return jsonify(dict(data=data)), 200

            # not found
            return jsonify(error='Not found'), 404

    def post(self):
        try:
            data = self.extract_data(request)
        except Exception as error:
            return jsonify(dict(error=str(error))), 400

        # process request
        try:
            id = self.source.add_data(name=data.get('name'), username=data.get('username'), email=data.get('email'))
        except sqlite3.Error as error:
            return jsonify(error=str(error)), 500
        else:
            return jsonify(dict(id=id)), 201

    def put(self, id):
        try:
            data = self.extract_data(request)
        except Exception as error:
            return jsonify(dict(error=str(error))), 400

        # process valid request
        try:
            self.source.update_data(
                id=id, name=data.get('name'), username=data.get('username'), email=data.get('email'))
        except sqlite3.Error as error:
            return jsonify(dict(error=str(error))), 500
        else:
            return '', 204

    def delete(self, id):
        try:
            self.source.delete_data(id)
        except sqlite3.Error as error:
            return jsonify(dict(error=str(error))), 500
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
