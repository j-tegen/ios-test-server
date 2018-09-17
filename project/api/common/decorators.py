from functools import wraps
from flask import request, g
from project.api.models import User
from .utils import make_response


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            return make_response(
                status_code=401,
                status='failure',
                message='Missing authorization header')
        try:
            auth_header = request.headers.get('Authorization')
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
        g.user_id = resp['sub']
        g.admin = resp['admin']
        return f(*args, **kwargs)
    return decorated_function
