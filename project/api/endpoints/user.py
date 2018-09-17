from flask import Blueprint
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models import User
from project.api.schemas import UserSchema
from project.api.common.decorators import login_required
from project.api.common.utils import make_response


bp_user = Blueprint('user', __name__)
user_schema = UserSchema()
users_schema = UserSchema(many=True)


user_args = {
    'id': fields.Integer(required=True, location='view_args')
}

save_args = {
    'name': fields.String(required=True),
    'email': fields.String(required=True),
    'phone_number': fields.String(),
}


@bp_user.route('/<id>', methods=['GET'])
@login_required
@use_args(user_args)
def get_user_detail(args, id):
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
@login_required
def get_user_list():
    users = User.query.all()
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=users_schema.dump(users).data)


@bp_user.route('/<id>', methods=['PUT'])
@login_required
@use_args(save_args)
def update_user(args, id):
    user = User.query.get(id)
    user.update(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated user',
        data=user_schema.dump(user).data)

