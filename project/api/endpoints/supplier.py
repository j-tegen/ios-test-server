from flask import Blueprint, g
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models import Supplier, Reclamation
from project.api.schemas import SupplierSchema, ReclamationSchema
from project.api.common.decorators import login_required, admin_required
from project.api.common.utils import make_response


bp_supplier = Blueprint('supplier', __name__)
supplier_schema = SupplierSchema()
suppliers_schema = SupplierSchema(many=True)


supplier_args = {
    'id': fields.Integer(required=True, location='view_args')
}

save_args = {
    'name': fields.String(required=True),
}


@bp_supplier.route('/<id>', methods=['GET'])
@login_required
@use_args(supplier_args)
def get_supplier_detail(args, id):
    supplier = Supplier.query.get(id)
    if not supplier:
        return make_response(
            status_code=404,
            status='failure',
            message='No supplier found with that id')
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=supplier_schema.dump(supplier).data)


@bp_supplier.route('/', methods=['GET'])
@login_required
def get_supplier_list():
    suppliers = Supplier.query.all()
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=suppliers_schema.dump(suppliers).data)



@bp_supplier.route('/', methods=['POST'])
@login_required
@use_args(save_args)
def create_supplier(args):
    supplier = Supplier(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated supplier',
        data=supplier_schema.dump(supplier).data)


@bp_supplier.route('/<id>', methods=['PUT'])
@login_required
@use_args(save_args)
def update_supplier(args, id):
    supplier = Supplier.query.get(id)
    supplier.update(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated supplier',
        data=supplier_schema.dump(supplier).data)


@bp_supplier.route('/<id>/reclamation', methods=['GET'])
@login_required
def get_reclamation_list(id):
    reclamations = Reclamation.query.filter_by(supplier_id=id).all()
    return make_response(
        status_code=200,
        status='success',
        data=ReclamationSchema(many=True).dump(reclamations).data)