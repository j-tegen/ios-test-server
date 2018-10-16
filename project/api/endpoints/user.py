from flask import Blueprint, g
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models import User, Reclamation
from project.api.schemas import UserSchema, ReclamationSchema
from project.api.common.decorators import login_required, admin_required
from project.api.common.utils import make_response


bp_user = Blueprint('user', __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)


user_args = {
    'id': fields.Integer(required=True, location='view_args')
}

password_args = {
    'password': fields.String(required=True)
}

save_args = {
    'name': fields.String(required=True),
    'email': fields.String(required=True),
    'phone_number': fields.String(),
}


@bp_user.route('/<id>', methods=['GET'])
@admin_required
@use_args(user_args)
def get_user_detail(args, id):
    """Admin"""
    user = User.query.get(id)
    if not user:
        return make_response(
            status_code=404,
            status='failure',
            message='No user found with that id')
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=user_schema.dump(user).data)


@bp_user.route('/', methods=['GET'])
@admin_required
def get_user_list():
    """Admin"""
    users = User.query.all()
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=users_schema.dump(users).data)


@bp_user.route('/<id>', methods=['PUT'])
@admin_required
@use_args(save_args)
def update_user(args, id):
    """Admin"""
    user = User.query.get(id)
    user.update(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated user',
        data=user_schema.dump(user).data)


@bp_user.route('/me', methods=['PUT'])
@login_required
def update_me():
    """Private"""
    user = User.query.get(g.user_id)
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=user_schema.dump(user).data)


@bp_user.route('/me', methods=['GET'])
@login_required
@use_args(save_args)
def get_me():
    """Private"""
    user = User.query.get(g.user_id)
    user.update(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=user_schema.dump(user).data)


# @bp_user.route('/<id>/reclamation', methods=['GET'])
# @login_required
# def get_reclamation_list(id):
#     """Private"""
#     reclamations = Reclamation.query.filter_by(user_id=id).all()
#     return make_response(
#         status_code=200,
#         status='success',
#         data=ReclamationSchema(many=True).dump(reclamations).data)


@bp_user.route('/<id>/change_password', methods=['PUT'])
@admin_required
@use_args(password_args)
def change_password(args, id):
    """Admin"""
    user = User.query.get(g.user_id)
    if not user:
        return make_response(
            status_code=404,
            status='failure',
            message='No user found with that id!')


    user.set_password(args['password'])
    db.session.add(user)
    db.session.commit()

    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=user_schema.dump(user).data)