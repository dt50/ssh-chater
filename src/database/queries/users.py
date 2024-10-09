from sqlalchemy.sql import exists
from typing import Sequence, List, Any, Hashable

import datetime
from database import engine, Session, User
from database.models.users import User, Session as UserSession


def get_user(nick_name) -> dict[Hashable, User|bool]:
    with Session(autoflush=False, bind=engine) as db:
        if not db.query(exists().where(User.username == nick_name)).scalar():
            return {"create": True, "user": create_user(nick_name)}
        else:
            user = db.query(User).filter(User.username == nick_name).scalar()
            user.last_entry = datetime.datetime.now()
            db.commit()
            return {"create": False, "user": db.query(User).filter(User.username == nick_name).scalar()}


def create_user(nick_name) -> User:
    with Session(autoflush=False, bind=engine) as db:
        user = User(
            username=nick_name,
            nick_name=nick_name,
        )
        db.add(user)
        db.commit()
        return user


def get_all_users():
    with Session(autoflush=False, bind=engine) as db:
        return db.query(User).all()
