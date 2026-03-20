"""Модуль для работы с данными."""
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql import select, delete, Select, or_
from sqlalchemy.exc import IntegrityError

import dataclasses
from collections import Counter
import typing as tp
from dataclasses import asdict
import logging

import tlibrary.database.models as models
from tlibrary.database.schemas import BookSchema, AuthorSchema, GenreSchema, AuxiliaryObjectSchema

logging.basicConfig(level=logging.DEBUG)


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

    def get_books(self, ids: tp.Sequence[int] | None = None, name: str | None = None, author_name: str | None = None,
                  genre_name: str | None = None, is_read: bool | None = None, year: int | None = None,
                  is_chosen: bool | None = None, order_by_year: bool = False, order_by_genre: bool = False,
                  order_by_author: bool = False, order_by_name: bool = False) -> list[BookSchema]:
        query = select(models.Book)
        if ids:
            query = query.where(models.Book.id.in_(ids))
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
        if order_by_name:
            query = query.order_by(models.Book.name)
        elif order_by_year:
            query = query.order_by(models.Book.year)
        elif order_by_genre:
            query = query.order_by(models.Book.genre)
        elif order_by_author:
            query = query.order_by(models.Book.author)

        with self._session() as session, session.begin():
            result = session.execute(query).scalars().all()
            schemas = []
            for model in result:  # Переделка в датаклассы
                model: models.Book
                schemas.append(BookSchema(name=model.name, description=model.description, year=model.year,
                                          is_chosen=model.is_chosen, is_read=model.is_read, author=model.author.name,
                                          genre=model.genre.name, id=model.id))
        return schemas

    def get_preferred_books(self) -> 'GetPreferredResponse':
        """Возвращает книги пользователя, соответствующие наиболее популярным авторам и жанрам среди его книг."""

        with self._session() as session, session.begin():
            books = self.get_books()
            if books:
                authors = Counter([book.author for book in books])
                genres = Counter([book.genre for book in books])

                most_common_author = authors.most_common(1)[0][0]
                most_common_genre = genres.most_common(1)[0][0]

                res_books = []
                for book in books:
                    if book.genre == most_common_genre or book.author == most_common_author:
                        res_books.append(book)
                return GetPreferredResponse(res_books, most_preferred_genre=most_common_genre,
                                            most_preferred_author=most_common_author)

    def add_books(self, schemas: tp.Sequence[BookSchema]):
        with self._session() as session, session.begin():
            data = []
            for schema in schemas:
                dict_ = asdict(schema)  # Превращаем в словарь и меняем параметры author и genre на author_id и genre_id
                dict_.update({self.author_id: schema.author, self.genre_id: schema.genre})
                dict_.pop(self.id)
                dict_.pop(self.author)
                dict_.pop(self.genre)
                data.append(models.Book(**dict_))

            session.add_all(data)

    def search_books(self, line: str):
        """Находит книги по вхождению строки в название, имя автора или описание."""

        with self._session() as session, session.begin():
            result = session.execute(select(models.Book).where(
                or_(models.Book.name.contains(line),
                    models.Book.author.has(models.Author.name.contains(line)),
                    models.Book.description.contains(line)
                    ))).scalars().all()
            schemas = []
            for model in result:  # Переделка в датаклассы
                model: models.Book
                schemas.append(BookSchema(name=model.name, description=model.description, year=model.year,
                                          is_chosen=model.is_chosen, is_read=model.is_read, author=model.author.name,
                                          genre=model.genre.name, id=model.id))

            return schemas

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
        try:
            self._add_auxiliaries(schemas, models.Author)
        except IntegrityError as e:  # Обработка ошибки уникальности
            if "UNIQUE constraint failed" in e.args[0]:
                raise NotUniqueValueError
            raise e

    def add_genres(self, schemas: tp.Sequence[GenreSchema]):
        try:
            self._add_auxiliaries(schemas, models.Genre)
        except IntegrityError as e:  # Обработка ошибки уникальности
            if "UNIQUE constraint failed" in e.args[0]:
                raise NotUniqueValueError
            raise e

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

    def get_authors(self) -> list[AuthorSchema]:
        with self._session() as session, session.begin():
            result = session.execute(select(models.Author)).scalars().all()
            if result:
                schemas = []
                for model in result:
                    schemas.append(AuthorSchema(name=model.name, id=model.id))
                return schemas
            else:
                return []

    def delete_books(self, ids: tp.Sequence[int]):
        with self._session() as session, session.begin():
            session.execute(delete(models.Book).where(models.Book.id.in_(ids)))

    def update_book(self, schema: BookSchema):
        """Обновляет книгу. В полях author и genre принимает ID соответствующего автора и жанра."""
        with self._session() as session, session.begin():
            result = session.execute(select(models.Book).where(models.Book.id == schema.id)).scalars().all()

            if result:
                model = result[0]
                model.name, model.author_id, model.genre_id = schema.name, schema.author, schema.genre
                model.description, model.year = schema.description, schema.year
                model.is_read, model.is_chosen = schema.is_read, schema.is_chosen


class BaseRepoException(Exception):
    pass


class NotUniqueValueError(BaseRepoException):
    pass


@dataclasses.dataclass
class GetPreferredResponse:
    """Ответ на получение предпочитаемых книг."""

    books: list[BookSchema]
    most_preferred_author: str
    most_preferred_genre: str


if __name__ == '__main__':
    pass
