from marshmallow import fields

from ..models import (
    User
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

    # reclamations = RelatedFromList(
    #     endpoint_list='reclamation.get_reclamation_list',
    #     endpoint_details='education.get_reclamation_detail',
    #     attribute='reclamations',
    #     dump_only=True)
