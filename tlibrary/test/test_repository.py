import pytest
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql import select

import typing as tp

from tlibrary.model import Repository, BaseSchema
from tlibrary.database.base_utils import launch_db, init_db
import tlibrary.database.models as cm


db_path = 'sqlite:///../database/database'


@pytest.fixture()
def add_books() -> sessionmaker:
    session_maker = init_db(db_path)

    with session_maker() as session, session.begin():
        genres = [cm.Genre(name=f'Genre#{i}{i % 2}') for i in range(10)]
        authors = [cm.Author(name=f'Author#{i}{i % 2}') for i in range(10)]
        session.add_all([*genres, *authors])
        get_genres = session.execute(select(cm.Genre).where(cm.Genre.name.contains('Genre'))).scalars().all()
        get_authors = session.execute(select(cm.Author).where(cm.Author.name.contains('Author'))).scalars().all()
        genres_ids = [model.id for model in get_genres]
        authors_ids = [model.id for model in get_authors]

        chosen_books = [cm.Book(name=f'Book#{i}{i % 2}', genre_id=i + genres_ids[0], author_id=i + authors_ids[0],
                                year=2025 + i % 2, is_chosen=True, is_read=bool(i % 2))
                        for i in range(10)]
        not_chosen_books = [cm.Book(name=f'Book#{i}{i % 2}', genre_id=i - 10 + genres_ids[0],
                                    author_id=i - 10 + authors_ids[0], year=2025 + i % 2, is_chosen=False,
                                    is_read=bool(i % 2))
                            for i in range(10, 21)]
        session.add_all([*chosen_books, *not_chosen_books])

    return session_maker


@pytest.fixture()
def repository_get(add_books) -> Repository:
    return Repository(add_books)


@pytest.mark.parametrize(
    ['getting_method', 'getting_params', 'expected_ids'],
    [
        [Repository.get_books, {'genre_name': 'Genre#00'}, [1, 11]],
        [Repository.get_books, {'is_chosen': True}, [i for i in range(1, 11)]]
    ]
)
def test_get(getting_method: tp.Callable[[Repository, tp.Any], list[BaseSchema]],
             getting_params: dict, repository_get: Repository, expected_ids: tp.Sequence[int]):
    result = getting_method(repository_get, **getting_params)
    ids = [schema.id for schema in result]
    assert tuple(ids) == tuple(expected_ids), repository_get.get_books()

