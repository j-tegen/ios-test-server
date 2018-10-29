from marshmallow import fields

from ..models import (
    User,
    Reclamation,
    Supplier,
    SupplierUserInfo,
    PaymentType,
    ReimbursementType,
    Station,
)
from project import ma
from .custom_fields import RelatedTo, RelatedFromQuery, RelatedFromList


class BaseSchema(ma.ModelSchema):
    id = fields.Integer(dump_to='_id')
    created = fields.DateTime(dump_only=True, dump_to='_created')
    timestamp = fields.DateTime(dump_only=True, dump_to='_timestamp')
    _descriptive = fields.String(dump_only=True)


class UserSchema(BaseSchema):
    class Meta:
        model = User
        exclude = ['password']

    skanetrafiken_user_info = RelatedTo(attribute='skanetrafiken_user_info')

    reclamations = RelatedFromList(
        endpoint_list='user.get_reclamation_list',
        endpoint_details='reclamation.get_reclamation_detail',
        attribute='reclamations',
        dump_only=True)


class ReclamationSchema(BaseSchema):
    class Meta:
        model = Reclamation

    refund = fields.Decimal(as_string=True)
    user = RelatedTo(attribute='user')
    supplier = RelatedTo(attribute='supplier')


class SupplierSchema(BaseSchema):
    class Meta:
        model = Supplier
        exclude = ['stations']

    payment_types = RelatedFromList(
        endpoint_list='supplier.get_payment_types',
        endpoint_details='payment_type.get_payment_type_detail',
        attribute='payment_types',
        dump_only=True)

    reimbursement_types = RelatedFromList(
        endpoint_list='supplier.get_reimbursement_types',
        endpoint_details='reimbursement_type.get_reimbursement_type_detail',
        attribute='reimbursement_types',
        dump_only=True)

    reclamations = RelatedFromList(
        endpoint_list='supplier.get_reclamation_list',
        endpoint_details='reclamation.get_reclamation_detail',
        attribute='reclamations',
        dump_only=True)


class SupplierUserInfoSchema(BaseSchema):
    class Meta:
        model = SupplierUserInfo

    payment_type = RelatedTo(attribute='payment_type')
    reimbursement_type = RelatedTo(attribute='reimbursement_type')
    supplier = RelatedTo(attribute='supplier')


class PaymentTypeSchema(BaseSchema):
    class Meta:
        model = PaymentType
        exclude = ['supplier_user_infos']


class ReimbursementTypeSchema(BaseSchema):
    class Meta:
        model = ReimbursementType
        exclude = ['supplier_user_infos']


class StationSchema(BaseSchema):
    class Meta:
        model = Station
