import datetime
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=None)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=None)
    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=None)
    position = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=None)
    speciality = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=None)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=None)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=True, default=None)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=None)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    avatar = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=None)

    news = orm.relationship("News", back_populates='user')
    jobs = orm.relationship("Jobs", back_populates='user')
    departments = orm.relationship("Department", back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
