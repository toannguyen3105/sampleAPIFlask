from db import db
from utils.date_format import getTimeStringFromTimeStamp
from sqlalchemy import desc


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True, comment="Username")
    password = db.Column(db.String(200), nullable=False, comment="Password")
    balance = db.Column(db.Integer, default=0, nullable=True, comment="Account balance")
    steam_id = db.Column(db.String(50), nullable=True, comment="Steam ID")
    active_code = db.Column(db.String(50), nullable=True, comment="Active code")
    active_code_expired_time = db.Column(db.Integer, nullable=True, comment="Expired time")
    ip = db.Column(db.String(100), nullable=True, comment="IP login")
    status = db.Column(db.SmallInteger, default=0, nullable=True, comment='0 is inactive, 1 active')
    attempted_login = db.Column(db.SmallInteger, default=0, nullable=True, comment='Maximum 5')
    attempted_buy = db.Column(db.SmallInteger, default=0, nullable=True, comment='Maximum 3')
    avatar = db.Column(db.String(200), nullable=True, comment="Avatar")
    email = db.Column(db.String(100), nullable=True, unique=True, comment="Email")
    phone = db.Column(db.String(50), nullable=True, comment="Phone")
    firstname = db.Column(db.String(50), nullable=True, comment="Firstname")
    lastname = db.Column(db.String(50), nullable=True, comment="Lastname")
    created_at = db.Column(db.Integer, nullable=True, comment="Timestamp")
    created_by = db.Column(db.String(30), nullable=True, comment="Timestamp")
    updated_at = db.Column(db.Integer, nullable=True, comment="Timestamp")
    updated_by = db.Column(db.String(30), nullable=True, comment="Timestamp")

    logs = db.relationship('LogModel', lazy='dynamic')
    items = db.relationship('ItemModel', lazy='dynamic')

    def __init__(self, username, password, balance, steam_id, active_code, active_code_expired_time, ip, status,
                 attempted_login, attempted_buy, avatar, email, phone, firstname, lastname, created_at, created_by,
                 updated_at, updated_by):
        self.username = username
        self.password = password
        self.balance = balance
        self.steam_id = steam_id
        self.active_code = active_code
        self.active_code_expired_time = active_code_expired_time
        self.ip = ip
        self.status = status
        self.attempted_login = attempted_login
        self.attempted_buy = attempted_buy
        self.avatar = avatar
        self.email = email
        self.phone = phone
        self.firstname = firstname
        self.lastname = lastname
        self.created_at = created_at
        self.created_by = created_by
        self.updated_at = updated_at
        self.updated_by = updated_by

    def json(self):
        return {
            'id': self.id,
            'username': self.username,
            'balance': self.balance,
            'steam_id': self.steam_id,
            'active_code': self.active_code,
            'active_code_expired_time': self.active_code_expired_time,
            'ip': self.ip,
            'status': self.status,
            'attempted_login': self.attempted_login,
            'attempted_buy': self.attempted_buy,
            'status_string': 'Active' if self.status == 1 else 'Inactive',
            'avatar': self.avatar,
            'email': self.email,
            'phone': self.phone,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'created_at': self.created_at,
            'created_at_string': None if self.created_at is None else getTimeStringFromTimeStamp(self.created_at),
            'created_by': self.created_by,
            'updated_at': self.updated_at,
            'updated_at_string': None if self.updated_at is None else getTimeStringFromTimeStamp(self.updated_at),
            'updated_by': self.updated_by
        }

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_active_code(cls, active_code):
        return cls.query.filter_by(active_code=active_code).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_all(cls):
        return cls.query.order_by(desc(cls.created_at)).all()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
