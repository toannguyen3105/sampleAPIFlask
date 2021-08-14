from db import db
from models.user import UserModel
from utils.date_format import getTimeStringFromTimeStamp
from sqlalchemy import desc

class TransactionModel(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    desc = db.Column(db.String(100))
    source = db.Column(db.String(100))
    status = db.Column(db.Integer, default=1, nullable=True, comment="0 là khởi tạo, 1 là thành công")
    created_at = db.Column(db.Integer, nullable=True, comment="Timestamp")
    created_by = db.Column(db.String(255), nullable=True, comment="Timestamp")
    updated_at = db.Column(db.Integer, nullable=True, comment="Timestamp")
    updated_by = db.Column(db.String(255), nullable=True, comment="Timestamp")

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('UserModel')

    def __init__(self, amount, desc, source, status, user_id, created_at, created_by, updated_at, updated_by):
        self.amount = amount
        self.desc = desc
        self.source = source
        self.status = status
        self.user_id = user_id
        self.created_at = created_at
        self.created_by = created_by
        self.updated_at = updated_at
        self.updated_by = updated_by

    def json(self):
        user = UserModel.find_by_id(self.user_id)

        return {
            'id': self.id,
            'amount': self.amount,
            'desc': self.desc,
            'source': self.source,
            'status': self.status,
            'user_id': self.user_id,
            'user_name': user.username if user else None,
            'created_at': self.created_at,
            'created_at_string': None if self.created_at is None else getTimeStringFromTimeStamp(self.created_at),
            'created_by': self.created_by,
            'updated_at': self.updated_at,
            'updated_at_string': None if self.updated_at is None else getTimeStringFromTimeStamp(self.updated_at),
            'updated_by': self.updated_by,
        }

    @classmethod
    def find_by_apikey(cls, apikey):
        return cls.query.filter_by(apikey=apikey).first()

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
    def q(cls, filters=None, order=None, order_by=None, page=0, page_size=10):
        search = "%{}%".format(filters) if filters is not None else "%%"
        return cls.query.filter(cls.desc.like(search)).order_by(cls.created_at.desc()).offset(page * page_size).limit(
            page_size).all()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
