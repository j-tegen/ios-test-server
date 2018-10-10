import requests
import string
import json
from project.api.models import Station, Supplier, PaymentType, ReimbursementType
from project import app, db, settings # noqa

SUPPLIER_KEY = 'skanetrafiken'
SUPPLIER_NAME = 'Skånetrafiken'
PAYMENT_TYPES = dict(jojo='Jojo-kort', app='App', cash='Kontant')
REIMBURSEMENT_TYPES = dict(voucher='Värdekupong', discount_code='Rabattkod')

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
    return supplier


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


def add_payment_types(supplier):
    for k, n in PAYMENT_TYPES.items():
        pament_type = PaymentType(**{
            'key': k,
            'name': n,
        })
        supplier.payment_types.append(pament_type)

    db.session.add(supplier)
    db.session.commit()


def add_reimbursement_types(supplier):
    for k, n in REIMBURSEMENT_TYPES.items():
        reimbursement_type = ReimbursementType(**{
            'key': k,
            'name': n,
        })
        supplier.reimbursement_types.append(reimbursement_type)

    db.session.add(supplier)
    db.session.commit()


def add_stations(supplier):
    stations = get_stations()


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

def setup_skanetrafiken():
    supplier = get_supplier()

    add_payment_types(supplier)
    add_reimbursement_types(supplier)
    add_stations(supplier)