from flask import Blueprint, request, g
from sqlalchemy import func
from webargs import fields
from webargs.flaskparser import use_args
from marshmallow import validate

from project import db
from project.api.models import (User, BlacklistToken)
from project.api.schemas import UserSchema
from project.api.common.decorators import login_required, admin_required
from project.api.common.utils import make_response

bp_auth = Blueprint('auth', __name__)
user_schema = UserSchema()

register_args = {
    'name': fields.String(required=True, validate=validate.Length(min=6, error='Name must be at least 6 characters long')),
    'email': fields.String(required=True, validate=validate.Email(error='Not a valid email address')),
    'password': fields.String(required=True, validate=validate.Length(min=6, error='Password must be at least 6 characters long')),
    'agreed_terms': fields.Boolean(required=True, validate=lambda p: p == True),
    'phone_number': fields.String(required=False),
    'social_security': fields.String(required=False),
}

login_args = {
    'email': fields.String(required=True),
    'password': fields.String(required=True)
}

password_args = {
    'password': fields.String(required=True)
}

token_args = {
    'email': fields.String(required=True),
}

logout_args = {
    'id': fields.Integer(required=True)
}


@bp_auth.route('/register', methods=['POST'])
@use_args(register_args)
def register(args):
    """Public"""
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
    """Public"""
    user = User.query.filter(
        func.lower(User.email) == func.lower(args['email'])).first()
    if not user:
        return make_response(
            status_code=404,
            status='failure',
            message='Invalid password and/or username.')
    if not user.check_password_hash(args['password']):
        return make_response(
            status_code=404,
            status='failure',
            message='Invalid password and/or username.')

    data = user_schema.dump(user).data
    auth_token = user.encode_auth_token(days=10000)
    data['auth_token'] = auth_token

    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=data)


@bp_auth.route('/change_password', methods=['PUT'])
@login_required
@use_args(password_args)
def change_password(args):
    """Private"""
    if not g.user_id:
        return make_response(
            status_code=404,
            status='failure',
            message='No user found for this session!')

    user = User.query.get(g.user_id)

    user.set_password(args['password'])
    db.session.add(user)
    db.session.commit()

    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=user_schema.dump(user).data)



@bp_auth.route('/create_integration_token', methods=['POST'])
@admin_required
@use_args(token_args)
def create_integration_token(args):
    """Admin"""
    user = User.query.filter(
        func.lower(User.email) == func.lower(args['email'])).first()
    if not user:
        return make_response(
            status_code=404,
            status='failure',
            message='Invalid email.')

    auth_token = user.encode_auth_token(days=100000)

    data = dict(auth_token=auth_token)
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=data)


@login_required
@bp_auth.route('/logout', methods=['POST'])
@use_args(login_args)
def logout(args):
    """Private"""
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
