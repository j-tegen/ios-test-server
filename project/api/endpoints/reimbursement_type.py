from flask import Blueprint, g
from webargs import fields
from webargs.flaskparser import use_args

from project import db, skanetrafiken
from project.api.models import ReimbursementType, Supplier
from project.api.schemas import ReimbursementTypeSchema
from project.api.common.decorators import login_required, admin_required
from project.api.common.utils import make_response


bp_reimbursement_type = Blueprint('reimbursement_type', __name__)
reimbursement_type_schema = ReimbursementTypeSchema()
reimbursement_types_schema = ReimbursementTypeSchema(many=True)

def get_suppliers():
    return [supplier.key for supplier in Supplier.query.all()]

list_args = {
    'supplier_key': fields.String(required=False, validate=lambda s: s in get_suppliers(), location='query')
}

reimbursement_type_args = {
    'id': fields.Integer(required=True, location='view_args')
}

save_args = {
    'name': fields.String(required=True),
    'key': fields.String(required=True)
}


@bp_reimbursement_type.route('/<id>', methods=['GET'])
@login_required
@use_args(reimbursement_type_args)
def get_reimbursement_type_detail(args, id):
    """Private"""
    reimbursement_type = ReimbursementType.query.get(id)
    if not reimbursement_type:
        return make_response(
            status_code=404,
            status='failure',
            message='No reimbursement_type found with that id')
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=reimbursement_type_schema.dump(reimbursement_type).data)


@bp_reimbursement_type.route('/', methods=['GET'])
@login_required
@use_args(list_args)
def get_reimbursement_type_list(args):
    """Private"""
    supplier = args.get('supplier', None)
    reimbursement_types = None
    if supplier:
        reimbursement_types = get_supplier_specific_list(supplier)
    else:
        reimbursement_types = ReimbursementType.query.all()

    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=reimbursement_types_schema.dump(reimbursement_types).data)


@bp_reimbursement_type.route('/<id>', methods=['PUT'])
@admin_required
@use_args(save_args)
def update_reimbursement_type(args, id):
    """Admin"""
    reimbursement_type = ReimbursementType.query.get(id)
    reimbursement_type.update(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated reimbursement_type',
        data=reimbursement_type_schema.dump(reimbursement_type).data)


@bp_reimbursement_type.route('/', methods=['POST'])
@admin_required
@use_args(save_args)
def create_reimbursement_type(args):
    """Admin"""
    reimbursement_type = ReimbursementType(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully created reimbursement_type',
        data=reimbursement_type_schema.dump(reimbursement_type).data)


SUPPLIER_REIMBURSEMENT_TYPES = dict(
    skanetrafiken=skanetrafiken.REIMBURSEMENT_TYPES
)

def get_supplier_specific_list(supplier):
    return ReimbursementType.query.filter(
        ReimbursementType.key.in_(SUPPLIER_REIMBURSEMENT_TYPES[supplier])).all()