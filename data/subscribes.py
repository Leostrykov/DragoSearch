import sqlalchemy
from .db_session import SqlAlchemyBase


class Subscribes(SqlAlchemyBase):
    __tablename__ = 'subscribes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    fav_user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('news.id'))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
