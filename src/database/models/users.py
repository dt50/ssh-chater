from sqlalchemy import Column, Integer, VARCHAR, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship, backref

import datetime

from .base import BaseModel

class User(BaseModel):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(VARCHAR(255), unique=True)

    nick_name = Column(VARCHAR(255), unique=True)

    last_entry = Column(TIMESTAMP, nullable=False, default=datetime.datetime.now())

    session_id = Column(Integer, ForeignKey('session.id'), unique=True)
    session = relationship("Session", backref=backref("user", uselist=False))

    def __repr__(self):
        return "<{0.__class__.__name__}(id={0.id!r}, username={0.username!r})>".format(self)


class Session(BaseModel):
    __tablename__ = 'session'

    id = Column(Integer, primary_key=True, autoincrement=True)
