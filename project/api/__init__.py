from flask import jsonify
from .endpoints.auth import bp_auth
from .endpoints.user import bp_user
from .endpoints.reclamation import bp_reclamation
from .endpoints.supplier import bp_supplier
from .. import app

ROOT_PREFIX = app.config['APPLICATION_ROOT']

def register_blueprints():
    app.register_blueprint(
        bp_auth,
        url_prefix='{}/{}'.format(ROOT_PREFIX, 'auth'))
    app.register_blueprint(
        bp_user,
        url_prefix='{}/{}'.format(ROOT_PREFIX, 'user'))
    app.register_blueprint(
        bp_reclamation,
        url_prefix='{}/{}'.format(ROOT_PREFIX, 'reclamation'))
    app.register_blueprint(
        bp_supplier,
        url_prefix='{}/{}'.format(ROOT_PREFIX, 'supplier'))

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
