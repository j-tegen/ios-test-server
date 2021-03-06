from flask import Blueprint, g
from webargs import fields
from webargs.flaskparser import use_args, use_kwargs

from project import db, skanetrafiken
from project.api.models import PaymentType, Supplier
from project.api.schemas import PaymentTypeSchema
from project.api.common.decorators import login_required, admin_required
from project.api.common.utils import make_response, filter_kwargs, create_filter


bp_payment_type = Blueprint('payment_type', __name__)
payment_type_schema = PaymentTypeSchema()
payment_types_schema = PaymentTypeSchema(many=True)


payment_type_args = {
    'id': fields.Integer(required=True, location='view_args')
}

save_args = {
    'name': fields.String(required=True),
    'key': fields.String(required=True)
}


@bp_payment_type.route('/<id>', methods=['GET'])
@login_required
def get_payment_type_detail(id):
    """Private"""
    payment_type = PaymentType.query.get(id)
    if not payment_type:
        return make_response(
            status_code=404,
            status='failure',
            message='No payment_type found with that id')
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=payment_type_schema.dump(payment_type).data)


@bp_payment_type.route('/', methods=['GET'])
@login_required
@use_kwargs(filter_kwargs)
def get_payment_type_list(**kwargs):
    """Private"""
    q = PaymentType.query
    q, count = create_filter(PaymentType, q, kwargs)
    payment_types = q.all()

    return make_response(
        status_code=200,
        status='success',
        message=None,
        count=count,
        data=payment_types_schema.dump(payment_types).data)


@bp_payment_type.route('/<id>', methods=['PUT'])
@admin_required
@use_args(save_args)
def update_payment_type(args, id):
    """Admin"""
    payment_type = PaymentType.query.get(id)
    payment_type.update(**args)
    db.session.add(payment_type)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated payment_type',
        data=payment_type_schema.dump(payment_type).data)


@bp_payment_type.route('/', methods=['POST'])
@admin_required
@use_args(save_args)
def create_payment_type(args):
    """Admin"""
    payment_type = PaymentType(**args)
    db.session.add(payment_type)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully created payment_type',
        data=payment_type_schema.dump(payment_type).data)
