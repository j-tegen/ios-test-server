import jwt
import datetime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import event, inspect, func
from flask import g
from sqlalchemy_utils.types.choice import ChoiceType

from project import app, db, bcrypt


class BaseMixin(object):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow())
    timestamp = db.Column(db.DateTime, nullable=False,
        default=datetime.datetime.utcnow())

    @hybrid_property
    def _descriptive(self):
        return self.id

    @_descriptive.expression
    def _descriptive(cls):
        return cls.id

    @hybrid_property
    def _key(self):
        return self.id

    @_key.expression
    def _key(cls):
        return cls.id

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @staticmethod
    def after_insert(mapper, connection, target):
        pass

    @staticmethod
    def after_update(mapper, connection, target):
        pass

    @staticmethod
    def before_update(mapper, connection, target):
        target.timestamp = datetime.datetime.utcnow()

    @staticmethod
    def before_insert(mapper, connection, target):
        pass

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, 'before_update', cls.before_update)
        event.listen(cls, 'before_insert', cls.before_insert)
        event.listen(cls, 'after_update', cls.after_update)
        event.listen(cls, 'after_insert', cls.after_insert)


class User(BaseMixin, db.Model):
    """ User Model for storing user related details """
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=True, unique=True)
    phone_number = db.Column(db.String(20), nullable=True)
    social_security = db.Column(db.String(20), nullable=True)
    registered_on = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.datetime.utcnow())

    admin = db.Column(db.Boolean, default=False)
    agreed_terms = db.Column(db.Boolean, default=False)

    @hybrid_property
    def _descriptive(self):
        return self.name

    @_descriptive.expression
    def _descriptive(cls):
        return cls.name

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.password = bcrypt.generate_password_hash(
            kwargs['password'], app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()

    def encode_auth_token(self, days=1):
        """
        Generates the Auth Token
        :return: string
        """
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=days),
            'iat': datetime.datetime.utcnow(),
            'sub': self.id,
            'admin': self.admin,
        }
        return jwt.encode(
            payload,
            app.config.get('SECRET_KEY'),
            algorithm='HS256'
        ).decode('utf-8')

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()

    def check_password_hash(self, password):
        return bcrypt.check_password_hash(self.password, password)

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False


supplier_payment_type = db.Table('supplier_payment_type',
    db.Column('supplier_id', db.Integer, db.ForeignKey('supplier.id'), primary_key=True),
    db.Column('payment_type_id', db.Integer, db.ForeignKey('payment_type.id'), primary_key=True)
)
supplier_reimbursement_type = db.Table('supplier_reimbursement_type',
    db.Column('supplier_id', db.Integer, db.ForeignKey('supplier.id'), primary_key=True),
    db.Column('reimbursement_type_id', db.Integer, db.ForeignKey('reimbursement_type.id'), primary_key=True)
)

class Supplier(BaseMixin, db.Model):
    __tablename__ = 'supplier'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    key = db.Column(db.String(50), nullable=False, unique=True)

    payment_types = db.relationship('PaymentType',
        secondary=supplier_payment_type,
        lazy='subquery',
        backref=db.backref('suppliers', lazy=True))

    reimbursement_types = db.relationship('ReimbursementType',
        secondary=supplier_reimbursement_type,
        lazy='subquery',
        backref=db.backref('suppliers', lazy=True))

    @hybrid_property
    def _descriptive(self):
        return self.name

    @_descriptive.expression
    def _descriptive(cls):
        return cls.name

    @hybrid_property
    def _key(self):
        return self.key

    @_key.expression
    def _key(cls):
        return cls.key


class Reclamation(BaseMixin, db.Model):
    __tablename__ = 'reclamation'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='reclamations')

    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    supplier = db.relationship('Supplier', backref='reclamations')

    expected_arrival = db.Column(db.DateTime, nullable=False)
    actual_arrival = db.Column(db.DateTime, nullable=False)
    delay = db.Column(db.Integer, default=0)
    vehicle_number = db.Column(db.String, nullable=True)
    booking_number = db.Column(db.String, nullable=True)

    from_station_id = db.Column(db.Integer, db.ForeignKey('station.id'))
    from_station =db.relationship('Station', foreign_keys=[from_station_id])
    to_station_id = db.Column(db.Integer, db.ForeignKey('station.id'))
    to_station =db.relationship('Station', foreign_keys=[to_station_id])

    payment_type_id = db.Column(db.Integer, db.ForeignKey('payment_type.id'))
    payment_type = db.relationship('PaymentType', backref='reclamations')
    reimbursement_type_id = db.Column(db.Integer, db.ForeignKey('reimbursement_type.id'))
    reimbursement_type = db.relationship('ReimbursementType', backref='reclamations')

    refund = db.Column(db.Numeric(10,2), nullable=False, default=0)
    approved = db.Column(db.Boolean, default=False)

    @hybrid_property
    def _descriptive(self):
        return "{created} - {supplier}".format(created=self.created, supplier=self.supplier.name)

    @_descriptive.expression
    def _descriptive(cls):
        return func.concat(cls.created, " ", cls.supplier.name)

    @staticmethod
    def before_update(mapper, connection, target):
        target.delay = (target.actual_arrival - target.expected_arrival).total_seconds() / 60


class PaymentType(BaseMixin, db.Model):
    __tablename__ = 'payment_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    key = db.Column(db.String, nullable=False, unique=True)

    @hybrid_property
    def _descriptive(self):
        return self.name

    @_descriptive.expression
    def _descriptive(cls):
        return cls.name

    @hybrid_property
    def _key(self):
        return self.key

    @_key.expression
    def _key(cls):
        return cls.key

class ReimbursementType(BaseMixin, db.Model):
    __tablename__ = 'reimbursement_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    key = db.Column(db.String, nullable=False, unique=True)

    @hybrid_property
    def _descriptive(self):
        return self.name

    @_descriptive.expression
    def _descriptive(cls):
        return cls.name

    @hybrid_property
    def _key(self):
        return self.key

    @_key.expression
    def _key(cls):
        return cls.key


class SupplierUserInfo(BaseMixin, db.Model):
    __tablename__ = 'supplier_user_info'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', uselist=False, backref='supplier_user_infos')
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    supplier = db.relationship('Supplier', backref='supplier_user_infos')

    payment_type_id = db.Column(db.Integer, db.ForeignKey('payment_type.id'))
    payment_type = db.relationship('PaymentType', backref='supplier_user_infos')

    reimbursement_type_id = db.Column(db.Integer, db.ForeignKey('reimbursement_type.id'))
    reimbursement_type = db.relationship('ReimbursementType', backref='supplier_user_infos')

    # Skånetrafiken specific
    jojo_number = db.Column(db.String)


class Station(BaseMixin, db.Model):
    __tablename__ = 'station'
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    supplier = db.relationship('Supplier', backref='stations')
    name = db.Column(db.String, nullable=False)
    migration_id = db.Column(db.String, nullable=False)

    @hybrid_property
    def _descriptive(self):
        return self.name

    @_descriptive.expression
    def _descriptive(cls):
        return cls.name


# # LOG ACTIVITIES
# # I.e. 'John Doe is interested in Cool project, BMW'
# # or   'Jane Doe was accepted for Cool project2, Volvo'
# @event.listens_for(db.Session, 'after_flush')
# def test(session, ctx):
#     for instance in session.dirty:
#         if not getattr(instance, 'add_activity', None):
#             print('nope')
#             continue
#         instance.add_activity(new=False, session=session)
#         print(instance)

#     for instance in session.new:
#         if not getattr(instance, 'add_activity', None):
#             print('nope')
#             continue
#         instance.add_activity(new=True, session=session)
#         print(instance)
