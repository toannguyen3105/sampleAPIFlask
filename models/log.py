from db import db
from utils.date_format import getTimeStringFromTimeStamp
from sqlalchemy import desc

class LogModel(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    ip_target = db.Column(db.String(30), nullable=True, comment="Ip of user")
    message = db.Column(db.String(100), nullable=False, comment="Action message")
    description = db.Column(db.String(300), nullable=False, comment="Description")
    status = db.Column(db.SmallInteger, default=0, nullable=True, comment='0 is inactive, 1 active')
    created_at = db.Column(db.Integer, nullable=True, comment="Timestamp create user")
    created_by = db.Column(db.String(30), nullable=True, comment="Person create user")
    updated_at = db.Column(db.Integer, nullable=True, comment="Timestamp update user")
    updated_by = db.Column(db.String(30), nullable=True, comment="Person update user")

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment="User do action")

    def __init__(self, user_id, ip_target, message, description, status, created_at, created_by, updated_at,
                 updated_by):
        self.user_id = user_id
        self.ip_target = ip_target
        self.message = message
        self.description = description
        self.status = status
        self.created_at = created_at
        self.created_by = created_by
        self.updated_at = updated_at
        self.updated_by = updated_by

    def json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ip_target': self.ip_target,
            'message': self.message,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at,
            'created_at_string': None if self.created_at is None else getTimeStringFromTimeStamp(self.created_at),
            'created_by': self.created_by,
            'updated_at': self.updated_at,
            'updated_at_string': None if self.updated_at is None else getTimeStringFromTimeStamp(self.updated_at),
            'updated_by': self.updated_by
        }

    @classmethod
    def find_by_message(cls, message):
        return cls.query.filter_by(message=message).first()

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_all(cls):
        return cls.query.order_by(desc(cls.created_at)).all()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
