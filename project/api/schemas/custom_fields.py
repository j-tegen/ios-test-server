from marshmallow import fields
from flask import url_for


class RelatedTo(fields.Field):
    def __init__(self, **kwargs):
        super(RelatedTo, self).__init__(**kwargs)

    def _serialize(self, value, attr, obj):
        if not value:
            return None
        return {
            '_id': value.id,
            '_descriptive': value._descriptive
        }


class RelatedFromQuery(fields.Field):
    def __init__(self, endpoint, **kwargs):
        super(RelatedFromQuery, self).__init__(**kwargs)
        self.endpoint = endpoint

    def _serialize(self, value, attr, obj):
        if not value:
            return []
        return [url_for(
            endpoint=self.endpoint,
            _external=True, id=item.id) for item in value]


class RelatedFromList(fields.Field):
    def __init__(self, endpoint_list, endpoint_details, **kwargs):
        super(RelatedFromList, self).__init__(**kwargs)
        self.endpoint_list = endpoint_list
        self.endpoint_details = endpoint_details

    def _serialize(self, value, attr, obj):
        print(value)
        print(attr)
        print(obj)
        print(self)
        if not value:
            return {
                '_collection': url_for(
                    endpoint=self.endpoint_list,
                    _external=True,
                    id=obj.id),
                '_items': []
            }

        return {
            '_collection': url_for(
                endpoint=self.endpoint_list,
                _external=True,
                id=obj.id),
            '_items': [self.get_item_dict(item) for item in value]
        }

    def get_item_dict(self, item):
        return {
            'url': url_for(
                endpoint=self.endpoint_details,
                _external=True,
                id=item.id),
            '_descriptive': item._descriptive
        }
