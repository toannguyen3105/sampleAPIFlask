from db import db
from utils.date_format import getTimeStringFromTimeStamp
from sqlalchemy import desc


class ConfigModel(db.Model):
    __tablename__ = 'configs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, comment="Title")
    description = db.Column(db.String(700), nullable=False, comment="Description")
    status = db.Column(db.SmallInteger, default=1, nullable=True, comment='0 is inactive, 1 active')
    created_at = db.Column(db.Integer, nullable=True, comment="Timestamp")
    created_by = db.Column(db.String(30), nullable=True, comment="Person")
    updated_at = db.Column(db.Integer, nullable=True, comment="Timestamp")
    updated_by = db.Column(db.String(30), nullable=True, comment="Person")

    def __init__(self, title, description, status, created_at, created_by, updated_at, updated_by):
        self.title = title
        self.description = description
        self.status = status
        self.created_at = created_at
        self.created_by = created_by
        self.updated_at = updated_at
        self.updated_by = updated_by

    def json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'status_string': 'Active' if self.status == 1 else 'Inactive',
            'created_at': self.created_at,
            'created_at_string': None if self.created_at is None else getTimeStringFromTimeStamp(self.created_at),
            'created_by': self.created_by,
            'updated_at': self.updated_at,
            'updated_at_string': None if self.updated_at is None else getTimeStringFromTimeStamp(self.updated_at),
            'updated_by': self.updated_by
        }

    @classmethod
    def find_by_name(cls, title):
        return cls.query.filter_by(title=title).first()

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
    def find_all_banner(cls):
        search_text = "BANNER"
        return cls.query.order_by(desc(cls.created_at)).filter(cls.title.ilike(f'%{search_text}%')).all()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
