from flask import Blueprint, g, url_for
from webargs import fields
from project import app

from project.api.common.decorators import login_required, admin_required
from project.api.common.utils import make_response


bp_admin = Blueprint('admin', __name__)

@bp_admin.route('/routes', methods=['GET'])
@admin_required
def list_routes():
    """Private"""
    from urllib.parse import unquote
    routes = []

    hidden_endpoints = ['static']
    relevant_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    for rule in app.url_map.iter_rules():
        if rule.endpoint in hidden_endpoints:
            continue
        options = {}
        for arg in rule.arguments:
            options[arg] = "<{0}>".format(arg)

        methods = ','.join(
            [method for method in rule.methods if method in relevant_methods])
        url = url_for(rule.endpoint, **options)
        url = url.replace('/api/v1/api/v1', '/api/v1')

        if hasattr(app.view_functions[rule.endpoint], 'import_name'):
            import_name = app.view_functions[rule.endpoint].import_name
            obj = import_string(import_name)
            line = dict(endpoint=rule.endpoint, methods=methods, url=url, access=obj.__doc__)
            routes.append(line)
        else:
            line = dict(endpoint=rule.endpoint, methods=methods, url=url, access=app.view_functions[rule.endpoint].__doc__)
            routes.append(line)

    return make_response(
        status_code=200,
        status='success',
        data=sorted(routes, key=lambda k:k['endpoint']))