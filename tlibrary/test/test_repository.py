import pytest
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql import select

import typing as tp

from tlibrary.model import Repository
from tlibrary.database.base_utils import init_db
import tlibrary.database.models as cm
from tlibrary.database.schemas import BaseSchema, BookSchema


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
                                year=2025 + i % 2, is_chosen=True, is_read=bool(i % 2), description=f'#{i % 2}')
                        for i in range(10)]
        not_chosen_books = [cm.Book(name=f'Book#{i}{i % 2}', genre_id=i - 10 + genres_ids[0],
                                    author_id=i - 10 + authors_ids[0], year=2025 + i % 2, is_chosen=False,
                                    is_read=bool(i % 2))
                            for i in range(10, 20)]
        session.add_all([*chosen_books, *not_chosen_books])

    return session_maker


@pytest.fixture()
def add_auxiliary() -> sessionmaker:
    session_maker = init_db(db_path)

    with session_maker() as session, session.begin():
        genres = [cm.Genre(name=f'Genre#{i}{i % 2}') for i in range(10)]
        authors = [cm.Author(name=f'Author#{i}{i % 2}') for i in range(10)]
        session.add_all([*genres, *authors])

    return session_maker


@pytest.fixture()
def repository_get(add_books) -> Repository:
    return Repository(add_books)


@pytest.fixture()
def repository_add(add_auxiliary) -> Repository:
    return Repository(add_auxiliary)


@pytest.mark.parametrize(
    ['getting_method', 'getting_params', 'expected_ids'],
    [
        [Repository.get_books, {'genre_name': 'Genre#00'}, [1, 11]],
        [Repository.get_books, {'is_chosen': True}, [i for i in range(1, 11)]],
        [Repository.get_books, {'author_name': 'Author#00'}, [1, 11]],
        [Repository.get_books, {'year': 2025}, [i for i in range(1, 21) if i % 2 != 0]],
        [Repository.get_books, {'year': 2026}, [i for i in range(1, 21) if i % 2 == 0]],
        [Repository.search_books, {'line': '#1'}, [2, 4, 6, 8, 10, *[i for i in range(11, 21)]]]
    ]
)
def test_get(getting_method: tp.Callable[[Repository, tp.Any], list[BaseSchema]],
             getting_params: dict, repository_get: Repository, expected_ids: tp.Sequence[int]):
    result = getting_method(repository_get, **getting_params)
    ids = [schema.id for schema in result]
    assert tuple(ids) == tuple(expected_ids), result


@pytest.mark.parametrize(
    ['adding_method', 'schemas', 'checking_method', 'checking_params', 'expected_ids'],
    [
        [  # К ID прибавляем 4, т.к. при инициализации БД создаётся 3 записи с жанрами
            Repository.add_books, [BookSchema(name='Book', description=None, year=2026, is_chosen=False,
                                   is_read=False, author=i % 2 + 1, genre=i % 2 + 4) for i in range(10)],
            Repository.get_books, {},
            [i for i in range(1, 11)]
        ],
        [
            Repository.add_books, [BookSchema(name='Book', description=None, year=2025, is_chosen=True,
                                              is_read=False, author=i % 2 + 1, genre=i % 2 + 4) for i in range(10)],
            Repository.get_books, {"genre_name": "Genre#00"}, [i for i in range(1, 11) if i % 2 != 0]
        ],
        [
            Repository.add_books, [BookSchema(name='Book', description=None, year=2025, is_chosen=True,
                                              is_read=False, author=i % 2 + 1, genre=i % 2 + 4) for i in range(10)],
            Repository.get_books, {"author_name": "Author#00"}, [i for i in range(1, 11) if i % 2 != 0]
        ],
        [
            Repository.add_books, [BookSchema(name='Book', description=None, year=2025, is_read=False,
                                              is_chosen=True if i % 4 == 0 else False, author=i % 2 + 1,
                                              genre=i % 2 + 4) for i in range(10)],
            Repository.get_books, {"author_name": "Author#00", "is_chosen": True}, [1, 5, 9]
        ]
    ]
)
def test_add(adding_method: tp.Callable[[Repository, tp.Any], tp.Any], schemas: tp.Sequence[BaseSchema],
             checking_method: tp.Callable[[Repository, tp.Any], tp.Any], checking_params: dict,
             expected_ids: tp.Sequence[int], repository_add: Repository):
    adding_method(repository_add, schemas)
    result = checking_method(repository_add, **checking_params)
    ids = [schema.id for schema in result]
    assert tuple(ids) == tuple(expected_ids)


@pytest.mark.parametrize(
    ["updating_method", "updating_params", "checking_method", "checking_params", "expected_ids"],
    [
        [
            Repository.change_status, {"book_id": 1, "status": True}, Repository.get_books, {"is_read": True},
            [1, *[i for i in range(1, 21) if i % 2 == 0]]
        ],
        [
            Repository.change_chosen, {"book_id": 11, "is_chosen": True}, Repository.get_books, {"is_chosen": True},
            [*[i for i in range(1, 11)], 11]
        ],
        [
            Repository.delete_books, {"ids": [i for i in range(1, 11)]}, Repository.get_books, {"is_chosen": True},
            []
        ],
        [
            Repository.delete_books, {"ids": [i for i in range(1, 11)]}, Repository.get_books,
            {"author_name": 'Author#00'}, [11]
        ]
    ],
)
def test_update(updating_method: tp.Callable[[Repository, tp.Any], tp.Any], updating_params: dict,
                checking_method: tp.Callable[[Repository, tp.Any], tp.Any], checking_params: dict,
                expected_ids: tp.Sequence[int], repository_get: Repository):
    updating_method(repository_get, **updating_params)
    result = checking_method(repository_get, **checking_params)
    ids = [schema.id for schema in result]
    assert tuple(ids) == tuple(expected_ids)
