from .models.base import Base

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .models.users import User

# строка подключения
sqlite_database = "sqlite:///test.db"
# создаем движок SqlAlchemy
engine = create_engine(sqlite_database)

# создаем таблицы
Base.metadata.create_all(bind=engine)

# # создаем сессию подключения к бд
# with Session(autoflush=False, bind=engine) as db:
#     # создаем объект Person для добавления в бд
#     tom = User(username="Tom")
#     db.add(tom)  # добавляем в бд
#     db.commit()  # сохраняем изменения
#     print(tom.id)  # можно получить установленный id