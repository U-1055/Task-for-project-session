"""Датаклассы моделей БД."""
from dataclasses import dataclass


@dataclass
class BaseSchema:
    pass


@dataclass
class BookSchema(BaseSchema):
    """Схема книги."""

    name: str
    description: str | None
    year: int
    is_chosen: bool
    is_read: bool

    author: str
    genre: str
    id: int | None = None


@dataclass
class AuxiliaryObjectSchema(BaseSchema):
    """Схема вспомогательных объектов (автор и жанр)"""

    name: str
    id: int | None = None


@dataclass
class AuthorSchema(AuxiliaryObjectSchema):
    pass


@dataclass
class GenreSchema(AuxiliaryObjectSchema):
    pass

