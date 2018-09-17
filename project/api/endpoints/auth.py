from flask import Blueprint, request
from sqlalchemy import func
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models import (User, BlacklistToken)
from project.api.schemas import UserSchema
from project.api.common.decorators import login_required
from project.api.common.utils import make_response

bp_auth = Blueprint('auth', __name__)
user_schema = UserSchema()

register_args = {
    'name': fields.String(required=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True),
    'agreed_terms': fields.Boolean(required=True, validate=lambda p: p == True),
    'phone_number': fields.String(required=False),
    'social_security': fields.String(required=False),
}

login_args = {
    'email': fields.String(required=True),
    'password': fields.String(required=True)
}

logout_args = {
    'id': fields.Integer(required=True)
}


@bp_auth.route('/register', methods=['POST'])
@use_args(register_args)
def register(args):
    print(args)
    user = User.query.filter(
        func.lower(User.email) == func.lower(args['email'])).first()
    if user:
        return make_response(
            status_code=409,
            status='failure',
            message='User already exists')
    user = User(**args)
    db.session.add(user)
    db.session.commit()

    data = user_schema.dump(user).data
    return make_response(
        status_code=200,
        status='success',
        message=None, data=data)


@bp_auth.route('/login', methods=['POST'])
@use_args(login_args)
def login(args):
    user = User.query.filter(
        func.lower(User.email) == func.lower(args['email'])).first()
    if not user:
        return make_response(
            status_code=404,
            status='failure',
            message='Invalid password and/or username and account.')
    if not user.check_password_hash(args['password']):
        return make_response(
            status_code=404,
            status='failure',
            message='Invalid password and/or username and account.')

    data = user_schema.dump(user).data
    auth_token = user.encode_auth_token(days=10000)
    data['auth_token'] = auth_token

    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=data)


@login_required
@bp_auth.route('/logout', methods=['POST'])
@use_args(login_args)
def logout(args):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return make_response(
            status_code=404,
            status='failure',
            message='No token was supplied. Could not identify user.')
    auth_token = auth_header.split(" ")[1]
    resp = User.decode_auth_token(auth_token)
    if isinstance(resp, str):
        return make_response(status_code=401, status='failure', message=resp)

    # Blacklist the token
    blacklist_token = BlacklistToken(token=auth_token)
    db.session.add(blacklist_token)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully logged out.')
