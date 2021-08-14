from db import db
from utils.date_format import getTimeStringFromTimeStamp
from sqlalchemy import desc

from models.user import UserModel

class ItemModel(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False, comment="Amount")
    steam_id = db.Column(db.String(50), nullable=False, comment="Steam ID")
    status = db.Column(db.SmallInteger, default=1, nullable=True, comment='0 is error, 1 is success')
    created_at = db.Column(db.Integer, nullable=True, comment="Timestamp")
    created_by = db.Column(db.String(30), nullable=True, comment="Person")
    updated_at = db.Column(db.Integer, nullable=True, comment="Timestamp")
    updated_by = db.Column(db.String(30), nullable=True, comment="Person")

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment="User")

    def __init__(self, amount, steam_id, user_id, status, created_at, created_by, updated_at, updated_by):
        self.amount = amount
        self.steam_id = steam_id
        self.user_id = user_id
        self.status = status
        self.created_at = created_at
        self.created_by = created_by
        self.updated_at = updated_at
        self.updated_by = updated_by

    def json(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'steam_id': self.steam_id,
            'user_id': self.user_id,
            'status': self.status,
            'status_string': 'Success' if self.status == 1 else 'Error',
            'created_at': self.created_at,
            'created_at_string': None if self.created_at is None else getTimeStringFromTimeStamp(self.created_at),
            'created_by': self.created_by,
            'updated_at': self.updated_at,
            'updated_at_string': None if self.updated_at is None else getTimeStringFromTimeStamp(self.updated_at),
            'updated_by': self.updated_by
        }

    def json_list(self, user):
        return {
            'id': self.id,
            'amount': self.amount,
            'steam_id': self.steam_id,
            'user_id': self.user_id,
            'user_name': user.username,
            'status': self.status,
            'status_string': 'Success' if self.status == 1 else 'Error',
            'created_at': self.created_at,
            'created_at_string': None if self.created_at is None else getTimeStringFromTimeStamp(self.created_at),
            'created_by': self.created_by,
            'updated_at': self.updated_at,
            'updated_at_string': None if self.updated_at is None else getTimeStringFromTimeStamp(self.updated_at),
            'updated_by': self.updated_by
        }

    @classmethod
    def find_by_name(cls, amount):
        return cls.query.filter_by(amount=amount).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_all(cls):
        return cls.query.order_by(desc(cls.created_at)).all()

    @classmethod
    def find_all_join(cls):
        return db.session.query(ItemModel, UserModel).join(UserModel).order_by(desc(cls.created_at)).all()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
