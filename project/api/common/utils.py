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
	'order_by': fields.String(required=False, location='query')
}


def make_response(status_code, status, message=None, data=None, count=0):
    response_content = dict(message=message, data=data, status=status, count=count)
    response = jsonify(
        {k: v for k, v in response_content.items() if v is not None})
    response.status_code = status_code
    return response


def create_filter(model, q, kwargs):
	filter_items = [item for item in kwargs.items() if item[1]]
	for attr, v in filter_items:
		f = getattr(model, attr, None)
		if not f:
			continue

		operator, val = v.split('__')
		print(operator, val)
		if operator == 'gte':
			q = q.filter(f >= val)
		elif operator == 'lte':
			q = q.filter(f <= val)
		elif operator == 'eq':
			q = q.filter(f == val)
		elif operator == 'neq':
			q = q.filter(f != val)
		elif operator == 'like':
			q = q.filter(f.ilike('%{}%'.format(val)))

	count = q.count()

	q = get_order_by(model, q, kwargs['order_by'])

	attr = kwargs['limit']
	if attr:
		q = q.limit(attr)

	q = q.offset(kwargs['offset'])

	return q, count


def get_order_by(model, q, v):
	if not v:
		return q

	operator, val = v.split('__')
	if not operator in ['asc', 'desc']:
		return q

	f = getattr(model, val, None)
	if not f:
		return q

	return q.order_by('{} {}'.format(val, operator))