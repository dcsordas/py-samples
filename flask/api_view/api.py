"""Object oriented REST API using View classes."""
import uuid

from flask import jsonify
from flask import request
from flask.views import MethodView

from lib import util

PORT = 8001


# view classes
class RootView(MethodView):
    """API root view."""

    @classmethod
    def register_view(cls, app, source=None):
        app.add_url_rule('/', view_func=cls.as_view('root'))

    def head(self):
        return '', 204


class AdminView(util.SourceView):
    """API data/ end point view."""

    @classmethod
    def register_view(cls, app, source):
        view = cls.as_view('/admin', source=source)
        app.add_url_rule(
            '/admin/users',
            view_func=view,
            defaults=dict(user_id=None),
            methods=('GET',))
        app.add_url_rule(
            '/admin/users/<int:user_id>',
            view_func=view,
            methods=('GET', 'PUT', 'DELETE'))
        app.add_url_rule(
            '/admin/users',
            view_func=view,
            methods=('POST',))

    def get(self, user_id):
        if user_id is None:

            # list usernames
            data = dict(data=sorted(self.source.get_usernames()))
            return jsonify(data), 200
        else:

            # get user
            data = self.source.get_user(user_id)
            if data:
                return jsonify(dict(data=data)), 200

            # not found
            return jsonify(error='data not found'), 404

    def post(self):
        try:
            name = request.form['name']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
        except KeyError:
            body = request.form
            return jsonify(body), 422
        salt = str(uuid.uuid4())
        password_hash = util.hash_password(password, salt)
        try:
            user_id = self.source.add_user(name, username, email, password_hash, salt)
            return jsonify(data=dict(id=user_id)), 201
        except util.DatabaseError:
            return jsonify(error='error registering user'), 500

    def put(self, user_id):
        if not request.form:
            return jsonify(dict(error='bad/no data in request')), 400
        try:
            self.source.update_user(
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

    def delete(self, user_id):
        try:
            self.source.delete_user(user_id)
        except util.DatabaseError:
            return jsonify(dict(error=str('data not deleted'))), 500
        else:
            return '', 204


# Flask application wrapper
class ApiServer(object):
    app = None
    views = (RootView, AdminView)

    def __init__(self, app):
        self.app = app

    def run(self, host, port):
        """
        Run server.

        :param host: server host
        :param port: server port
        """
        self.app.run(host, port)
