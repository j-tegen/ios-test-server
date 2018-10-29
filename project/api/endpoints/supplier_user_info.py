from flask import Blueprint, g
from webargs import fields
from webargs.flaskparser import use_args

from project import db, skanetrafiken
from project.api.models import SupplierUserInfo, Supplier, User
from project.api.schemas import SupplierUserInfoSchema
from project.api.common.decorators import login_required, admin_required
from project.api.common.utils import make_response


bp_supplier_user_info = Blueprint('supplier_user_info', __name__)
supplier_user_info_schema = SupplierUserInfoSchema()
supplier_user_infos_schema = SupplierUserInfoSchema(many=True)


supplier_user_info_args = {
    'id': fields.Integer(required=True, location='view_args')
}

save_args = {
    'supplier_id': fields.Integer(required=True),
    'jojo_number': fields.String(required=False),
    'payment_type_id': fields.Integer(required=False),
    'reimbursement_type_id': fields.Integer(required=False),
}

@bp_supplier_user_info.route('/', methods=['PUT'])
@admin_required
@use_args(save_args)
def add_or_update_supplier_user_info(args):
    """Private"""
    supplier_user_info = SupplierUserInfo.query.filter_by(
        user_id=g.user_id, supplier_id=args['supplier_id']).first()

    if not supplier_user_info:
        supplier_user_info = SupplierUserInfo(**{
            **args,
            **{'user_id': g.user_id}
        })
    else:
        supplier_user_info.update(**args)
    db.session.add(supplier_user_info)
    db.session.commit()
    return make_response(
        status_code=200,
        status='success',
        message='Successfully updated supplier_user_info',
        data=supplier_user_info_schema.dump(supplier_user_info).data)
