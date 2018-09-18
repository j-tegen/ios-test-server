from marshmallow import fields

from ..models import (
    User,
    Reclamation,
    Supplier
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

    user = RelatedTo(attribute='user')
    supplier = RelatedTo(attribute='supplier')


class SupplierSchema(BaseSchema):
    class Meta:
        model = Supplier

    reclamations = RelatedFromList(
        endpoint_list='supplier.get_reclamation_list',
        endpoint_details='reclamation.get_reclamation_detail',
        attribute='reclamations',
        dump_only=True)
