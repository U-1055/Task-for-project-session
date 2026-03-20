from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from sqlalchemy import ForeignKey
from sqlalchemy.types import String


class Base(DeclarativeBase):

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class Book(Base):
    __tablename__ = 'book'

    author_id: Mapped[int] = mapped_column(ForeignKey('author.id'))
    genre_id: Mapped[int] = mapped_column(ForeignKey('genre.id'))

    # Могут быть две книги с одним именем, но разными авторами\жанрами
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(String(2000), nullable=True)
    year: Mapped[int] = mapped_column()
    is_chosen: Mapped[bool] = mapped_column(default=False)
    is_read: Mapped[bool] = mapped_column(default=False)

    author: Mapped['Author'] = relationship('Author', back_populates='books')
    genre: Mapped['Genre'] = relationship('Genre', back_populates='books')


class Genre(Base):
    __tablename__ = 'genre'
    # Двух авторов\жанров с одинаковыми именами не может быть
    name: Mapped[str] = mapped_column(String(150), unique=True)
    books: Mapped[list[Book]] = relationship('Book', back_populates='genre')


class Author(Base):
    __tablename__ = 'author'

    name: Mapped[str] = mapped_column(String(150), unique=True)
    books: Mapped[list[Book]] = relationship('Book', back_populates='author')

