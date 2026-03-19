"""Функции для работы с БД."""
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

import enum

from tlibrary.database.models import Base, Genre


class DataConst(enum.Enum):

    unread = 'Не прочитана'
    read = 'Прочитана'
    scientific = 'Научная фантастика'
    fantasy = 'Фэнтези'
    historical = 'История'

    default_db_path = 'sqlite:///tlibrary/database/database'


def init_db(path: str) -> sessionmaker:
    """Создаёт базу заново и возвращает sessionmaker."""
    engine = create_engine(path)
    session_maker = sessionmaker(bind=engine)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    with session_maker() as session, session.begin():
        genres = [Genre(name=DataConst.fantasy.value), Genre(name=DataConst.historical.value), Genre(name=DataConst.scientific.value)]
        session.add_all(genres)

    return session_maker


def launch_db(path: str) -> sessionmaker:
    """Запускает базу и возвращает sessionmaker."""
    engine = create_engine(path)
    session_maker = sessionmaker(bind=engine)

    return session_maker


if __name__ == '__main__':
    pass
