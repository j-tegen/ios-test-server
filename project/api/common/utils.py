from flask import jsonify
from webargs import fields


FIELDS = ['created', 'timestamp', '_id', '_key', '_descriptive']


filter_kwargs = {
    'created': fields.String(required=False, location='query'),
    'timestamp': fields.String(required=False, location='query'),
    '_key': fields.String(required=False, location='query'),
    '_descriptive': fields.String(required=False, location='query'),
    'limit': fields.Integer(required=False, location='query', missing=None),
    'offset': fields.Integer(required=False, location='query', missing=0),
}


def make_response(status_code, status, message=None, data=None, count=0):
    response_content = dict(message=message, data=data, status=status, count=count)
    response = jsonify(
        {k: v for k, v in response_content.items() if v is not None})
    response.status_code = status_code
    return response


def create_filter(model, q, kwargs):
	filter_items = [item for item in kwargs.items() if item[1] and item[0] in FIELDS]
	for attr, v in filter_items:
		operator, val = v.split('__')
		f = getattr(model, attr)
		if operator == 'gte':
			q = q.filter(f >= val)
		elif operator == 'lte':
			q = q.filter(f <= val)
		elif operator == 'eq':
			q = q.filter(f == val)
		elif operator == 'neq':
			q = q.filter(f != val)
		elif operator == 'like':
			q = q.filter(f.like('%{}%'.format(val)))

	count = q.count()
	attr = kwargs['limit']
	if attr:
		q = q.limit(attr)

	q = q.offset(kwargs['offset'])
	return q, count