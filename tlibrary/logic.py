import dataclasses

from tlibrary.console_manager import (ConsoleManager, MainMenu, BooksMenu, BookCreatingMenu, ChooseMenu,
                                      SearchMenu, PreferredBooksMenu, StatusFilterMenu)
from tlibrary.model import Repository, NotUniqueValueError
from tlibrary.database.base_utils import DataConst
from tlibrary.database.schemas import BookSchema, AuthorSchema, GenreSchema

import logging
import typing as tp

logging.basicConfig(level=logging.DEBUG)

# ToDo: убрать логи
# ToDo: получение наиболее частого жанра - так сделаем предпочтения


class IncorrectInputException(Exception):

    def __init__(self, message: str):
        self.message = message


class Logic:
    """Класс логики приложения."""

    ADD = 'ADD'
    UPDATE = 'UPDATE'

    CHOSEN = 'CHOSEN'
    COMMON = 'COMMON'
    SEARCH = 'SEARCH'
    PREFERENCES = 'PREFERENCES'

    # Названия полей

    settings = 'settings'
    sort_type = 'sort_type'  # Тип сортировки

    # Настройки сортировки и фильтрации

    filter_by_status = 'filter_by_status'

    only_read = 'only_read'  # Только прочитанные
    only_unread = 'only_unread'  # Только непрочитанные
    any_ = 'any'  # Любые

    name_lbl_mapping = {
        only_read: ConsoleManager.only_read, only_unread: ConsoleManager.only_unread,
        any_: ConsoleManager.any_
    }

    lbl_name_mapping = {
        ConsoleManager.only_read: only_read, ConsoleManager.only_unread: only_unread,
        ConsoleManager.any_: any_
    }

    def __init__(self, console_manager: ConsoleManager, repo: Repository):
        self._repo = repo
        self._view = console_manager

        self._book_creating_menu: BookCreatingMenu | None = None  # Меню редактирования книги
        self._choosing_menu: ChooseMenu | None = None  # Меню авторов\жанров
        self._searching_menu: SearchMenu | None = None  # Меню для поиска книг
        self._last_menu_type: str | None = None

        # Настройки сортировки
        self._settings = ViewSettings()

        self._on_main_menu()

    def _show_books_menu(self, is_chosen: bool | None = None):
        """Выводит меню книг."""
        logging.debug(f'Settings: {self._settings}')
        getting_params = {"is_read": None, "is_chosen": True if is_chosen else None}
        filter_param = None

        if self._settings.filter_by_status:
            if self._settings.filter_by_status == self.only_read:
                getting_params["is_read"] = True
            elif self._settings.filter_by_status == self.only_unread:
                getting_params["is_read"] = False
        logging.debug(f"Params: {getting_params}")
        books = self._repo.get_books(**getting_params)

        books_menu = BooksMenu(None,
                               None, self.name_lbl_mapping.get(self._settings.filter_by_status))
        logging.debug(books_menu)
        if is_chosen:  # Если меню для Избранного, то нужно убрать пункт "Новая книга"
            books_menu.name = ConsoleManager.chosen
            books_menu.filter_by_status_id = 2
            books_menu.set_item(2, ConsoleManager.filter_by_status, {self._on_filter_by_status_chosen})
            books_menu.delete_item(3)
            books_menu.clear_separators()
            books_menu.set_separator(books_menu.filter_by_status_id, ConsoleManager.books)

        books_menu.add_callback_to_main_menu_chosen(self._on_main_menu)
        books_menu.add_callback_filter_by_status_chosen(self._on_filter_by_status_chosen)

        if not is_chosen:
            books_menu.add_callback_create_new_book(self._on_create_new_book_chosen)

        if self._settings.filter_by_status:
            books_menu.filter_by_status = self.name_lbl_mapping.get(self._settings.filter_by_status)

        if books:
            count = books_menu.count()

            # Если элементов больше двух, будем учитывать следующий
            for i in range(len(books)):
                num = i + 1 + count
                books_menu.set_item(num, books[i].name, {lambda id_=books[i].id: self._on_book_chosen(id_)})

            logging.debug(books_menu.menu)
        if is_chosen:
            self._last_menu_type = self.CHOSEN
        else:
            self._last_menu_type = self.COMMON

        self._view.show_menu(books_menu)

    def _set_book_creating_menu(self, is_creating_type: bool) -> BookCreatingMenu:
        menu = BookCreatingMenu(is_creating_type=is_creating_type)
        menu.add_callback_edit_name_chosen(self._on_edit_name_chosen)
        menu.add_callback_edit_genre_chosen(self._on_edit_genre_chosen)
        menu.add_callback_edit_year_chosen(self._on_edit_year_chosen)
        menu.add_callback_edit_author_chosen(self._on_edit_author_chosen)
        menu.add_callback_edit_description(self._on_edit_description_chosen)
        menu.add_callback_change_status_chosen(self._on_change_status_chosen)
        menu.add_callback_change_chosen_chosen(self._on_change_chosen_chosen)
        menu.add_callback_cancel_and_return_chosen(self._on_cancel_and_return_chosen)
        if not is_creating_type:
            menu.add_callback_delete_book_chosen(self._on_delete_book_chosen)

        return menu

    def _on_preferences_chosen(self):
        response = self._repo.get_preferred_books()
        if response:
            books_menu = PreferredBooksMenu(response.most_preferred_author, response.most_preferred_genre)
            count = books_menu.count()
            for i in range(len(response.books)):
                num = i + 1 + count
                books_menu.set_item(num, response.books[i].name, {lambda id_=response.books[i].id: self._on_book_chosen(id_)})
        else:
            books_menu = PreferredBooksMenu()

        books_menu.add_callback_to_main_menu_chosen(self._on_main_menu)
        self._last_menu_type = self.PREFERENCES
        self._view.show_menu(books_menu)

    def _on_filter_by_status_chosen(self):
        filter_menu = StatusFilterMenu()
        filter_menu.add_callback_to_books_menu_chosen(self._choose_books_menu)
        filter_menu.add_callback_any_chosen(lambda: self._on_filter_type_changed(ConsoleManager.any_, filter_menu))
        filter_menu.add_callback_only_unread_chosen(lambda: self._on_filter_type_changed(ConsoleManager.only_unread, filter_menu))
        filter_menu.add_callback_only_read_chosen(lambda: self._on_filter_type_changed(ConsoleManager.only_read, filter_menu))
        current_filter = self.name_lbl_mapping.get(self._settings.filter_by_status)
        filter_menu.current_filter_type = current_filter if current_filter else ConsoleManager.any_
        self._view.show_menu(filter_menu)

    def _on_filter_type_changed(self, filter_type: str, filter_menu: StatusFilterMenu):
        filter_menu.current_filter_type = filter_type
        self._settings.filter_by_status = self.lbl_name_mapping.get(filter_type)
        logging.debug(f'CHANGED SETTING: {self._settings}. FILTER: {filter_type}')

    def _on_book_chosen(self, book_id: int):
        """Обрабатывает выбор книги в меню книг."""

        menu = self._set_book_creating_menu(False)
        menu.add_callback_save_and_return_chosen(lambda: self._record_book_to_db(self.UPDATE))
        menu.id = book_id

        result = self._repo.get_books(ids=[book_id])
        if result:
            schema = result[0]
            menu.name, menu.book_description, menu.genre = schema.name, schema.description, schema.genre
            menu.author, menu.year = schema.author, schema.year
            menu.status = schema.is_read
            menu.chosen = schema.is_chosen
            menu.is_changed = False
            self._book_creating_menu = menu
            logging.debug(schema.is_chosen, schema.is_read)
        self._view.show_menu(menu)

    def _on_delete_book_chosen(self):
        line = self._view.get_data(ConsoleManager.confirm_delete_book).strip()
        if line == 'Y' and self._book_creating_menu and self._book_creating_menu.id:
            self._repo.delete_books([self._book_creating_menu.id])
            self._book_creating_menu = None
            self._choose_books_menu()

    def _on_create_new_book_chosen(self):
        menu = self._set_book_creating_menu(True)
        menu.add_callback_save_and_return_chosen(lambda: self._record_book_to_db(self.ADD))
        self._book_creating_menu = menu
        self._view.show_menu(menu)

    def _record_book_to_db(self, type_: str = tp.Literal['ADD', 'UPDATE']):
        try:
            self._check_fields()
            author_name = self._book_creating_menu.author
            genre_name = self._book_creating_menu.genre
            author = self._repo.get_author(author_name)
            genre = self._repo.get_genre(genre_name)
            if not author:
                logging.critical(f"THERE IS NO AUTHOR: {author}. Menu: {self._book_creating_menu}")
                raise IncorrectInputException(f"Автора {author_name} не сущеcтвует.")
            if not genre:
                logging.critical(f"THERE IS NO GENRE: {genre}. Menu: {self._book_creating_menu}")
                raise IncorrectInputException(f"Жанра {genre_name} не существует.")

            schema = BookSchema(name=self._book_creating_menu.name, description=self._book_creating_menu.book_description,
                                year=self._book_creating_menu.year, author=author.id, genre=genre.id,
                                is_read=self._book_creating_menu.status,
                                is_chosen=self._book_creating_menu.chosen)
            if type_ == self.UPDATE:
                schema.id = self._book_creating_menu.id
            logging.debug(schema)
            if type_ == self.ADD:
                self._repo.add_books([schema])
            elif type_ == self.UPDATE:
                self._repo.update_book(schema)
            else:
                logging.critical(f"UNKNOWN TYPE: {type_}")
            self._book_creating_menu = None
            self._view.show_text(ConsoleManager.book_is_saved)
            self._choose_books_menu()
        except IncorrectInputException as e:
            self._view.show_text(e.message)

    def _on_cancel_and_return_chosen(self):
        if self._book_creating_menu and self._book_creating_menu.is_changed:
            line = self._view.get_data(ConsoleManager.confirm_cancel).strip()
            if line == 'Y':
                self._book_creating_menu = None
                self._choose_books_menu()
        else:
            self._book_creating_menu = None
            self._choose_books_menu()

    def _on_edit_name_chosen(self):
        if self._book_creating_menu:
            new_name = self._view.get_data(f'{ConsoleManager.enter_new_book_name}: ')
            if new_name:
                self._book_creating_menu.name = new_name.strip()

    def _on_edit_description_chosen(self):
        if self._book_creating_menu:
            new_desc = self._view.get_data(f'{ConsoleManager.enter_new_book_description}: ')
            self._book_creating_menu.book_description = new_desc.strip()

    def _on_edit_author_chosen(self):
        if self._book_creating_menu:
            author_menu = ChooseMenu(ConsoleManager.author_menu, ConsoleManager.choose_author)
            author_menu.add_callback_return_to_book_chosen(self._show_book_creating_menu)
            author_menu.set_item(author_menu.add_object, ConsoleManager.add_author, {self._on_add_author_chosen})

            authors = [schema.name for schema in self._repo.get_authors()]
            count = author_menu.count()
            for i, author in enumerate(authors):
                author_menu.set_item(i + 1 + count, author,
                                     {lambda author_=author: self._on_author_chosen(author_)})

            self._choosing_menu = author_menu
            self._view.show_menu(author_menu)

    def _on_edit_genre_chosen(self):
        if self._book_creating_menu:
            genre_menu = ChooseMenu(ConsoleManager.genre_menu, ConsoleManager.choose_genre)
            genre_menu.add_callback_return_to_book_chosen(self._show_book_creating_menu)
            genre_menu.set_item(genre_menu.add_object, ConsoleManager.add_genre, {self._on_add_genre_chosen})

            genres = [schema.name for schema in self._repo.get_genres()]
            count = genre_menu.count()
            for i, genre in enumerate(genres):
                genre_menu.set_item(i + 1 + count, genre, {lambda genre_=genre: self._on_genre_chosen(genre_)})

            self._choosing_menu = genre_menu
            self._view.show_menu(genre_menu)

    def _on_edit_year_chosen(self):
        if self._book_creating_menu:
            new_year = self._view.get_int(f'{ConsoleManager.enter_new_book_year}: ')
            self._book_creating_menu.year = new_year

    def _on_change_chosen_chosen(self):
        item = self._book_creating_menu.get_item(self._book_creating_menu.choose)
        if item.name == ConsoleManager.cancel_choose:
            self._book_creating_menu.chosen = False
        elif item.name == ConsoleManager.choose:
            self._book_creating_menu.chosen = True
        else:
            logging.critical(f"INCORRECT CHOSEN VARIANT: {item.name}")
        logging.debug(f'Set new CHOSEN status: {self._book_creating_menu.chosen}')

    def _on_change_status_chosen(self):
        item = self._book_creating_menu.get_item(self._book_creating_menu.mark_as_read)
        if item.name == ConsoleManager.mark_as_unread:
            self._book_creating_menu.status = False
        elif item.name == ConsoleManager.mark_as_read:
            self._book_creating_menu.status = True
        else:
            logging.critical(f"INCORRECT STATUS VARIANT: {item.name}")
        logging.debug(f'Set new READ status: {self._book_creating_menu.status}')

    def _on_add_author_chosen(self):
        if self._choosing_menu:
            new_author = self._view.get_data(f'{ConsoleManager.enter_new_author}: ')
            if new_author:
                try:
                    self._repo.add_authors([AuthorSchema(name=new_author)])
                    last_item_num = self._choosing_menu.count()
                    self._choosing_menu.set_item(last_item_num + 1, new_author,
                                                 {lambda: self._on_author_chosen(new_author)})
                except NotUniqueValueError as e:
                    self._view.show_text(ConsoleManager.author_already_exists)

    def _on_add_genre_chosen(self):
        if self._choosing_menu:
            new_genre = self._view.get_data(f'{ConsoleManager.enter_new_genre}: ')
            if new_genre:
                try:
                    self._repo.add_genres([GenreSchema(name=new_genre)])
                    last_item_num = self._choosing_menu.count()
                    self._choosing_menu.set_item(last_item_num + 1, new_genre,
                                                 {lambda: self._on_genre_chosen(new_genre)})
                except NotUniqueValueError as e:
                    self._view.show_text(ConsoleManager.genre_already_exists)

    def _on_search_books_menu_chosen(self):
        books_menu = SearchMenu()
        books_menu.add_callback_search_books_chosen(self._on_search_books_chosen)
        books_menu.add_callback_to_main_menu_chosen(self._on_main_menu)
        self._searching_menu = books_menu
        self._last_menu_type = self.SEARCH
        self._view.show_menu(self._searching_menu)

    def _on_search_books_chosen(self):
        line = self._view.get_data(f'{ConsoleManager.enter_search}: ').strip()
        if line and self._searching_menu:
            self._set_searched_to_menu(line)

    def _on_exit_chosen(self):
        line = self._view.get_data(ConsoleManager.confirm_exit).strip()
        if line == 'Y':
            exit(-1)

    def _on_main_menu(self):
        menu = MainMenu()
        menu.add_callback_my_books_chosen(self._show_books_menu)
        menu.add_callback_chosen_chosen(lambda: self._show_books_menu(True))
        menu.add_callback_search_book_chosen(self._on_search_books_menu_chosen)
        menu.add_callback_exit_chosen(self._on_exit_chosen)
        menu.add_callback_preferences_chosen(self._on_preferences_chosen)
        self._view.show_menu(menu)

    def _on_author_chosen(self, author: str):
        """Выбран автор в меню авторов."""
        if self._book_creating_menu:
            self._book_creating_menu.author = author
            self._show_book_creating_menu()

    def _on_genre_chosen(self, genre: str):
        """Выбран жанр в меню жанров."""
        if self._book_creating_menu:
            self._book_creating_menu.genre = genre
            self._show_book_creating_menu()

    def _check_fields(self):
        """Проверяет ввод данных в форму для книги. Вызывает исключение IncorrectInputException при ошибках."""
        if not self._book_creating_menu:
            logging.critical(f"There is no book creating menu!!!. Book creating menu: {self._book_creating_menu}")
            raise IncorrectInputException("Unknown Error. Try to rerun the application.")

        if not self._book_creating_menu.genre:
            raise IncorrectInputException("Нужно выбрать жанр")
        if not self._book_creating_menu.author:
            raise IncorrectInputException("Нужно выбрать автора")
        if not self._book_creating_menu.year:
            raise IncorrectInputException("Нужно указать год издания")

        if len(self._book_creating_menu.name) > DataConst.max_name_length.value:
            raise IncorrectInputException(f"Слишком длинное название книги ({len(self._book_creating_menu.name)} символов)"
                                          f" - допустимо {DataConst.max_name_length.value} или меньше.")
        if len(self._book_creating_menu.description) > DataConst.max_description_length.value:
            raise IncorrectInputException(f"Слишком длинное описание ({len(self._book_creating_menu.name)} символов)"
                                          f" - допустимо {DataConst.max_description_length.value} или меньше.")

    def _show_book_creating_menu(self):
        if self._book_creating_menu:
            if self._choosing_menu:
                self._choosing_menu = None

            self._view.show_menu(self._book_creating_menu)
    
    def _show_searching_menu(self, clear: bool = False):
        if self._searching_menu:
            if clear:
                self._searching_menu.clear()
            self._view.show_menu(self._searching_menu)

    def _set_searched_to_menu(self, line: str):
        """Устанавливает результаты поиска в меню поиска."""
        self._searching_menu.searching_line = line
        self._searching_menu.clear()
        books = self._repo.search_books(line)
        count = self._searching_menu.count()

        for i in range(len(books)):
            num = i + 1 + count
            self._searching_menu.set_item(num, books[i].name, {lambda id_=books[i].id: self._on_book_chosen(id_)})
        self._view.show_text(f"Найдено {len(books)} книг" if len(books) else "Ничего не найдено :(")

    def _choose_books_menu(self):
        """Выбирает меню книг, исходя из last_menu_type."""
        if self._last_menu_type == self.COMMON:
            self._show_books_menu(False)
        elif self._last_menu_type == self.CHOSEN:
            self._show_books_menu(True)
        elif self._last_menu_type == self.SEARCH:
            if self._searching_menu:
                if self._searching_menu.searching_line:
                    self._set_searched_to_menu(self._searching_menu.searching_line)
                self._show_searching_menu()
            else:
                self._on_search_books_menu_chosen()
        elif self._last_menu_type == self.PREFERENCES:
            self._on_preferences_chosen()


@dataclasses.dataclass
class ViewSettings:
    """Настройки отображения книг."""
    filter_by_status: str | None = None
