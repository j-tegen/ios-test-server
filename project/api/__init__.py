from flask import jsonify
from .endpoints.auth import bp_auth
from .endpoints.user import bp_user
from .. import app


def register_blueprints():
    app.register_blueprint(
        bp_auth,
        url_prefix='{}/{}'.format(app.config['APPLICATION_ROOT'], 'auth'))
    app.register_blueprint(
        bp_user,
        url_prefix='{}/{}'.format(app.config['APPLICATION_ROOT'], 'user'))

def register_error_handlers():
    @app.errorhandler(422)
    def handle_unprocessable_entity(err):
        exc = getattr(err, 'exc')
        if exc:
            messages = exc.messages
        else:
            messages = ['Invalid request']
        return jsonify({
            'status': 'error',
            'result': messages
        }), 422
