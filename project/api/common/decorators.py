from functools import wraps
from flask import request, g
from project.api.models import User
from .utils import make_response


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Token'):
            return make_response(
                status_code=401,
                status='failure',
                message='Missing authorization header')
        try:
            auth_header = request.headers.get('Token')
            auth_token = auth_header.split(" ")[1]
        except IndexError:
            return make_response(
                status_code=401,
                status='failure',
                message='Bearer token malformed')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, str):
                return make_response(
                    status_code=401,
                    status='failure',
                    message=resp)
            g.user_id = resp.get('sub', None)
            g.admin = resp.get('admin', None)
            return f(*args, **kwargs)
        return make_response(
            status_code=401,
            status='Could not authenticate user',
            message=resp)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Token'):
            return make_response(
                status_code=401,
                status='failure',
                message='Missing authorization header')
        try:
            auth_header = request.headers.get('Token')
            auth_token = auth_header.split(" ")[1]
        except IndexError:
            return make_response(
                status_code=401,
                status='failure',
                message='Bearer token malformed')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if isinstance(resp, str):
                return make_response(
                    status_code=401,
                    status='Could not authenticate user',
                    message=resp)

            if not resp.get('admin', None):
                return make_response(
                    status_code=401,
                    status='This endpoint requires admin authorization'
                )
            g.user_id = resp.get('sub', None)
            g.admin = resp.get('admin', None)
            return f(*args, **kwargs)
        return make_response(
                    status_code=401,
                    status='Could not authenticate user',
                    message=resp)
    return decorated_function
