from flask import Blueprint, g
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models import Reclamation
from project.api.schemas import ReclamationSchema
from project.api.common.decorators import login_required, admin_required
from project.api.common.utils import make_response


bp_reclamation = Blueprint('reclamation', __name__)
reclamation_schema = ReclamationSchema()
reclamations_schema = ReclamationSchema(many=True)


reclamation_args = {
    'id': fields.Integer(required=True, location='view_args')
}

save_args = {
    'approved': fields.Boolean(required=True),
    'expected_arrival': fields.DateTime(format='iso', required=True),
    'actual_arrival': fields.DateTime(format='iso', required=True),
    'vehicle_number': fields.String(required=False),
    'refund': fields.Float(required=False),
    'supplier_id': fields.Integer(required=True),
}


@bp_reclamation.route('/<id>', methods=['GET'])
@login_required
@use_args(reclamation_args)
def get_reclamation_detail(args, id):
    """Private"""
    reclamation = Reclamation.query.get(id)
    if not reclamation:
        return make_response(
            status_code=404,
            status='failure',
            message='No reclamation found with that id')
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=reclamation_schema.dump(reclamation).data)


@bp_reclamation.route('/', methods=['GET'])
@admin_required
def get_reclamation_list():
    """Admin"""
    reclamations = Reclamation.query.all()
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=reclamations_schema.dump(reclamations).data)


@bp_reclamation.route('/<id>', methods=['PUT'])
@login_required
@use_args(save_args)
def update_reclamation(args, id):
    """Private"""
    reclamation = Reclamation.query.get(id)
    reclamation.update(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated reclamation',
        data=reclamation_schema.dump(reclamation).data)


@bp_reclamation.route('/', methods=['POST'])
@login_required
@use_args(save_args)
def create_reclamation(args):
    """Private"""
    reclamation = Reclamation(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully created reclamation',
        data=reclamation_schema.dump(reclamation).data)