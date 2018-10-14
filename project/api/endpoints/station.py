from flask import Blueprint, g
from sqlalchemy import desc, func
from webargs import fields
from webargs.flaskparser import use_args

from project import db
from project.api.models import Station, Reclamation
from project.api.schemas import StationSchema, ReclamationSchema
from project.api.common.decorators import login_required, admin_required
from project.api.common.utils import make_response


bp_station = Blueprint('station', __name__)
station_schema = StationSchema()
stations_schema = StationSchema(many=True)


station_args = {
    'id': fields.Integer(required=True, location='view_args')
}

stations_args = {
    'filter': fields.String(required=True, validate=lambda k: len(k) > 1),
    'supplier_key': fields.String(required=True, location='query')
}


@bp_station.route('/<id>', methods=['GET'])
@login_required
@use_args(station_args)
def get_station_detail(args, id):
    """Private"""
    station = Station.query.get(id)
    if not station:
        return make_response(
            status_code=404,
            status='failure',
            message='No station found with that id')
    return make_response(
        status_code=200,
        status='success',
        message=None,
        data=station_schema.dump(station).data)


@bp_station.route('/', methods=['GET'])
@login_required
@use_args(stations_args)
def get_station_list(args):
    """Private"""
    filter_str = '%{}%'.format(args['filter'])
    stations = Station.query.filter(
        Station.supplier.has(key=args['supplier_key']),
        Station.name.ilike(filter_str)).order_by(
            func.similarity(Station.name, args['filter']).desc()
        ).all()

    return make_response(
        status_code=200,
        status='success',
        message='This method has been replaced by "../supplier/<id>/station/ and should be considered deprecated.',
        data=stations_schema.dump(stations).data)
