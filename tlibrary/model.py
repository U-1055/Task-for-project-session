"""Модуль для работы с данными."""
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import Query
from sqlalchemy.sql import select, insert, delete, update, Select

from pathlib import Path
import shelve
import typing as tp
from dataclasses import asdict
import logging

import tlibrary.database.models as models
from tlibrary.database.schemas import BookSchema, BaseSchema, AuthorSchema, GenreSchema, AuxiliaryObjectSchema

logging.basicConfig(level=logging.DEBUG)


class Model:
    """Класс для операций с файлом настроек (shelve DB)."""

    # Названия полей

    settings = 'settings'
    type_sort = 'type_sort'  #  Тип сортировки

    # Допустимые значения полей

    enabled = 'enabled'
    disabled = 'disabled'

    # Настройки сортировки и фильтрации

    sort_author = 'sort_author'  # Значения для сортировки
    sort_genre = 'sort_genre'
    sort_year = 'sort_year'

    only_read = 'only_read'  # Только прочитанные
    only_unread = 'only_unread'  # Только непрочитанные

    _struct = {
        settings: {
            only_read: False, only_unread: False, sort_year: None, sort_genre: None, sort_author: None
        }
    }

    def __init__(self, path: Path):
        self._path = path
        self._validate()

    def _validate(self):
        if not self._path.is_file():
            with shelve.open(self._path) as storage:
                storage = self._struct

    def get_settings(self):
        pass


class Repository:
    """Класс для операций с БД."""

    author_id = 'author_id'
    genre_id = 'genre_id'
    name = 'name'
    description = 'description'
    year = 'year'
    is_chosen = 'is_chosen'
    is_read = 'is_read'
    id = 'id'
    author = 'author'
    genre = 'genre'

    # ToDo: метод получения книг + остальные CRUD'ы + сериализация прямо в репе с заменой отношений на имена сущностей
    def __init__(self, session_maker: sessionmaker):
        self._session = session_maker

    def _get(self, query: Select) -> list[models.Base]:
        with self._session() as session, session.begin():
            result = session.execute(query).scalars().all()
            return [model for model in result]

    def _add_auxiliaries(self, schemas: tp.Sequence[AuxiliaryObjectSchema], base_model: tp.Type[models.Base]):
        with self._session() as session, session.begin():
            models_ = [base_model(name=schema.name) for schema in schemas]
            session.add_all(models_)

    def get_books(self, name: str | None = None, author_name: str | None = None, genre_name: str | None = None,
                  is_read: bool | None = None, year: int | None = None, is_chosen: bool | None = None) -> list[BookSchema]:
        query = select(models.Book)
        if name:
            query = query.where(models.Book.name == name)
        if author_name:
            query = query.where(models.Book.author.has(models.Author.name == author_name))
        if genre_name:
            query = query.where(models.Book.genre.has(models.Genre.name == genre_name))
        if is_read is not None:
            query = query.where(models.Book.is_read == is_read)
        if is_chosen is not None:
            query = query.where(models.Book.is_chosen == is_chosen)
        if year:
            query = query.where(models.Book.year == year)

        with self._session() as session, session.begin():
            result = session.execute(query).scalars().all()
            schemas = []
            for model in result:  # Переделка в датаклассы
                model: models.Book
                schemas.append(BookSchema(name=model.name, description=model.description, year=model.year,
                                          is_chosen=model.is_chosen, is_read=model.is_read, author=model.author.name,
                                          genre=model.genre.name, id=model.id))
        return schemas

    def add_books(self, schemas: tp.Sequence[BookSchema]):
        with self._session() as session, session.begin():
            authors = {model.id: model for model in session.execute(select(models.Author)).scalars().all()}
            genres = {model.id: model for model in session.execute(select(models.Genre)).scalars().all()}
            data = []
            logging.info(f"authors: {authors}\ngenres: {genres}\nschemas: {schemas}\n----------------------")
            for schema in schemas:
                dict_ = asdict(schema)  # Превращаем в словарь и меняем параметры author и genre на author_id и genre_id
                dict_.update({self.author_id: schema.author, self.genre_id: schema.genre})
                dict_.pop(self.id)
                dict_.pop(self.author)
                dict_.pop(self.genre)
                data.append(models.Book(**dict_))

            session.add_all(data)

    def get_author(self, name: str) -> AuthorSchema | None:
        query = select(models.Author).where(models.Author.name == name)
        with self._session() as session, session.begin():
            result = session.execute(query).scalars().all()
            if result:
                author = AuthorSchema(id=result[0].id, name=result[0].name,)
                return author

    def get_genre(self, name: str) -> GenreSchema:
        query = select(models.Genre).where(models.Genre.name == name)
        with self._session() as session, session.begin():
            result = session.execute(query).scalars().all()
            if result:
                genre = GenreSchema(id=result[0].id, name=result[0].name, )
                return genre

    def add_authors(self, schemas: tp.Sequence[AuthorSchema]):
        self._add_auxiliaries(schemas, models.Author)

    def add_genres(self, schemas: tp.Sequence[GenreSchema]):
        self._add_auxiliaries(schemas, models.Genre)

    def change_status(self, book_id: int, status: bool):
        """
        Меняет статус книге.

        :param book_id: ID книги.
        :param status: Новый статус книги. True - прочитана, False - нет.

        """
        with self._session() as session, session.begin():
            result = session.execute(select(models.Book).where(models.Book.id == book_id)).scalars().all()
            if result:
                book = result[0]
                book.is_read = status

    def change_chosen(self, book_id: int, is_chosen: bool):
        with self._session() as session, session.begin():
            result = session.execute(select(models.Book).where(models.Book.id == book_id)).scalars().all()
            if result:
                book = result[0]
                book.is_chosen = is_chosen

    def get_genres(self) -> list[GenreSchema]:
        with self._session() as session, session.begin():
            result = session.execute(select(models.Genre)).scalars().all()
            if result:
                schemas = []
                for model in result:
                    schemas.append(GenreSchema(name=model.name, id=model.id))
                return schemas
            else:
                return []


if __name__ == '__main__':
    from tlibrary.database.base_utils import init_db
    repo = Repository(init_db('sqlite:///database/database'))
    authors = [AuthorSchema(name) for name in ["Gashek", "Zhukov", "Vdovin"]]
    repo.add_authors(authors)

    genre_id = repo.get_genre('Фэнтези').id
    author_id = repo.get_author('Vdovin').id

    books = [BookSchema("Imperium of Mankind. The Great Country.", "Описание отсутствует", 42002, False, False,
                        author_id, genre_id)]
    print(genre_id, author_id)
    repo.add_books(books)
    print(repo.get_books())
    repo.change_status(1, True)
    print(repo.get_books())
    repo.change_chosen(1, True)
    print(repo.get_books())

