import requests
import string
import json
from project.api.models import Station, Supplier
from project import app, db, settings # noqa

SUPPLIER_KEY = 'skanetrafiken'
SUPPLIER_NAME = 'Skånetrafiken'
PAYMENT_TYPES = ['jojo', 'app', 'cash']

def get_supplier():
    supplier = Supplier.query.filter_by(key=SUPPLIER_KEY).first()

    if supplier:
        return supplier

    supplier = Supplier(**{
        'name': SUPPLIER_NAME,
        'key': SUPPLIER_KEY
    })
    db.session.add(supplier)
    db.session.commit()


def get_stations():
    base_url = 'https://www.skanetrafiken.se/handlers/LocationSearch.ashx?action=search&q={}'
    letters = string.ascii_lowercase + 'åäö'
    queries = [val1 + val2 for val1 in letters for val2 in letters]
    data = []

    for query in queries:
        response = requests.get(base_url.format(query))
        if not response:
            continue

        data = data + response.json().get('StartEndPoint', [])

    stations = [d for d in data if d['Type'] == 'STOP_AREA']
    return list({v['Id']:v for v in stations}.values())


def add_stations():
    stations = get_stations()
    supplier = get_supplier()

    for s in stations:
        station = Station.query.filter_by(migration_id=str(s['Id']), supplier_id=supplier.id).first()
        if station:
            continue
        station = Station(**{
            'name': s['Name'],
            'supplier_id': supplier.id,
            'migration_id': str(s['Id'])
        })
        db.session.add(station)

    db.session.commit()