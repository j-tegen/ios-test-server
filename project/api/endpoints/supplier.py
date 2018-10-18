from flask import Blueprint, g
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models import Supplier, Reclamation, PaymentType, ReimbursementType
from project.api.schemas import SupplierSchema, ReclamationSchema, PaymentTypeSchema, ReimbursementTypeSchema
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
    'key': fields.String(required=True)
}

stations_args = {
    'filter': fields.String(),
}

reclamation_args = {
    'approved': fields.Boolean(required=True),
    'expected_arrival': fields.DateTime(format='iso', required=True),
    'actual_arrival': fields.DateTime(format='iso', required=True),
    'vehicle_number': fields.String(required=False),
    'refund': fields.Float(required=False),
}


@bp_supplier.route('/<id>', methods=['GET'])
@login_required
@use_args(supplier_args)
def get_supplier_detail(args, id):
    """Private"""
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
    """Private"""
    suppliers = Supplier.query.all()
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=SupplierSchema(many=True, exclude=['supplier_user_infos']).dump(suppliers).data)



@bp_supplier.route('/', methods=['POST'])
@admin_required
@use_args(save_args)
def create_supplier(args):
    """Admin"""
    supplier = Supplier(**args)
    db.session.add(supplier)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated supplier',
        data=supplier_schema.dump(supplier).data)


@bp_supplier.route('/<id>', methods=['PUT'])
@admin_required
@use_args(save_args)
def update_supplier(args, id):
    """Admin"""
    supplier = Supplier.query.get(id)
    supplier.update(**args)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated supplier',
        data=supplier_schema.dump(supplier).data)


@bp_supplier.route('/<id>', methods=['DELETE'])
@admin_required
def delete_supplier(id):
    """Admin"""
    supplier = Supplier.query.get(id)
    db.session.delete(supplier)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated supplier',
        data=id)


@bp_supplier.route('/<id>/reclamation', methods=['GET'])
@login_required
def get_reclamation_list(id):
    """Private"""
    reclamations = Reclamation.query.filter_by(supplier_id=id).all()
    return make_response(
        status_code=200,
        status='success',
        data=ReclamationSchema(many=True).dump(reclamations).data)


@bp_supplier.route('/<id>/payment_types', methods=['GET'])
@login_required
def get_payment_types(id):
    """Private"""

    payment_types = Supplier.query.get(id).payment_types
    return make_response(
        status_code=200,
        status='success',
        data=PaymentTypeSchema(many=True).dump(payment_types).data)


@bp_supplier.route('/<id>/reimbursement_types', methods=['GET'])
@login_required
def get_reimbursement_types(id):
    """Private"""

    reimbursement_types = Supplier.query.get(id).reimbursement_types
    return make_response(
        status_code=200,
        status='success',
        data=ReimbursementTypeSchema(many=True).dump(reimbursement_types).data)


@bp_supplier.route('/<id>/station', methods=['GET'])
@login_required
@use_args(stations_args)
def get_station_list(args, id):
    """Private"""
    filter_str = '%{}%'.format(args['filter'])
    stations
    if args.get('filter', None):
        stations = Station.query.filter(
            Station.supplier.has(id=id),
            Station.name.ilike(filter_str)).order_by(
                func.similarity(Station.name, args['filter']).desc()
            ).all()
    else:
        stations = Supplier.query.get(id).stations

    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=stations_schema.dump(stations).data)


@bp_supplier.route('/<id>/reclamation', methods=['POST'])
@login_required
@use_args(reclamation_args)
def create_reclamation(args, id):
    """Private"""
    supplier = Supplier.query.get(id)
    reclamation = Reclamation(**args)
    reclamation.user_id = g.user_id
    supplier.reclamations.append(reclamation)
    db.session.add(supplier)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully created reclamation',
        data=ReclamationSchema().dump(reclamation).data)