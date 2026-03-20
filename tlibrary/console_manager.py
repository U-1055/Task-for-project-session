
import typing as tp
from dataclasses import dataclass


class ConsoleManager:
    """Класс для управления выводом на консоль."""

    lbl_enter_menu_item = 'Введите номер пункта меню: '
    lbl_incorrect_int = 'Введите корректное целое число'
    lbl_no_menu_num = 'В меню нет такого пункта'

    # Названия меню

    main_menu = 'Главное меню'
    books_menu = 'Мои книги'
    new_book = 'Новая книга'
    author_menu = 'Авторы'
    genre_menu = 'Жанры'

    separator = '-------------------------------------------------------'
    menu_padding = '\n\n\n'

    # Пункты меню

    my_books = "Мои книги"
    chosen = 'Избранное'
    search_books = 'Найти книги'
    exit_ = 'Выйти из приложения'
    create_new_book = 'Новая книга'
    to_main_menu = 'В Главное меню'
    sort_books = 'Сортировать книги'

    delete_book = 'Удалить книгу'
    save_and_return = 'Сохранить и вернуться'
    cancel_and_return = 'Отменить и вернуться'
    edit_name = 'Изменить название'
    edit_description = 'Изменить описание'
    edit_author = 'Изменить автора'
    edit_genre = 'Изменить жанр'
    edit_year = 'Изменить год издания'
    choose = 'Добавить в Избранное'
    cancel_choose = 'Убрать из Избранного'
    mark_as_read = 'Пометить прочитанной'
    mark_as_unread = 'Пометить непрочитанной'

    return_to_book = 'Вернуться к редактированию'
    add_genre = 'Добавить жанр'
    add_author = 'Добавить автора'

    # Описания меню

    choose_book = 'Выберите книгу или добавьте новую'
    choose_author = 'Выберите автора или добавьте нового'
    choose_genre = 'Выберите жанр или добавьте новый'
    search = 'Поиск книг по ключевым словам в названии, имени автора и описании'

    # Прочие надписи
    title_book_search = 'Поиск'
    enter_search = 'Введите строку для поиска'
    sort = 'Сортировка'
    filtration_by_genre = 'Жанр'
    filtration_by_status = 'Статус'
    book_is_saved = 'Книга успешно сохранена'
    enter_new_book_name = "Введите новое название книги (не более 150 символов)"
    enter_new_book_description = 'Введите новое описание книги (не более 2000)'
    enter_new_book_year = 'Введите год издания'
    enter_new_author = 'Введите нового автора'
    enter_new_genre = 'Введите новый жанр'
    author_already_exists = 'Такой автор уже существует'
    genre_already_exists = 'Такой жанр уже существует'

    confirm_delete_book = 'Вы уверены, что хотите удалить книгу? ([Y] - ДА, любая другая клавиша - НЕТ): '
    confirm_exit = 'Вы уверены, что хотите выйти? ([Y] - ДА, любая другая клавиша - НЕТ): '
    confirm_cancel = 'Вы уверены, что хотите отменить изменения? ([Y] - ДА, любая другая клавиша - НЕТ):'
    genre = 'Жанр'
    author = 'Автор'
    status = 'Статус'
    year = 'Год издания'
    is_chosen = 'В Избранном'
    is_not_chosen = 'Нет в Избранном'
    description = 'Описание'
    is_read = 'Прочитана'
    is_not_read = 'Не прочитана'
    sort_by_author = 'По автору'
    sort_by_name = 'По имени'
    sort_by_genre = 'По жанру'
    sort_by_year = 'По году'
    no_sort = 'Нет'

    def __init__(self):
        self._current_menu: 'Menu' | None = None
        print("Приветствуем Вас в Т-библиотеке!")
        input("Нажмите любую клавишу, чтобы запустить приложение")

    def _get_current_menu_data(self):
        """Ожидает ввод пункта текущего меню."""

        input_ = self.get_int(self.lbl_enter_menu_item)
        if self._current_menu:  # Если есть меню
            if input_ in self._current_menu.menu:  # Вызов коллбэков
                [callback() for callback in self._current_menu.menu[input_].callbacks]
            else:
                print(self.lbl_no_menu_num)
        self.show_menu(self._current_menu)

    def show_menu(self, menu: 'Menu'):
        """Переключает меню."""
        if self._current_menu:
            print(self.menu_padding)
        print(self.separator)
        print(f'Раздел: {menu.name}')
        print(self.separator)
        if menu.description:
            print(menu.description)
            print(self.separator)

        self._current_menu = menu
        for item_ in (sorted(list(menu.menu.keys()))):  # Выводим в порядке возрастания (ВСЕ КЛЮЧИ - целые числа)
            print(f'{item_}. {menu.menu[item_].name}')
            if item_ in self._current_menu.separators:
                print(self._current_menu.separators[item_])

        print(self.separator)
        self._get_current_menu_data()

    def get_data(self, label: str) -> str:
        return input(label)

    def get_int(self, label: str) -> int:
        try:
            return int(input(label))
        except ValueError:
            print(f"{self.lbl_incorrect_int}\n")
            return self.get_int(label)

    def show_text(self, text: str):
        print(text)


class Menu:
    """Меню."""

    def __init__(self, name: str, description: str | None = None, menu_data: dict[int, 'MenuItem'] = None):
        self._menu = menu_data if menu_data else {}
        self._separators: dict[int, 'Separator'] = {}  # Разделители участков меню
        self.name = name
        self._description = description

    def set_item(self, num: int, name: str, callbacks: set[tp.Callable]):
        self._menu[num] = MenuItem(num, name, callbacks)

    def delete_item(self, num: int):
        if num in self._menu:
            self._menu.pop(num)

    def get_item(self, num: int) -> 'MenuItem':
        return self._menu.get(num)

    def set_separator(self, num: int, text: str, line_char: str = '-'):
        """
        Добавляет разделитель после пункта меню под номером num.

        :param num: Номер пункта меню, после которого будет добавлен разделитель.
        :param text: Текст разделителя.
        :param line_char: Символ линии разделителя (Если "-", будет "-----" и т.д.).

        """
        self._separators[num] = Separator(text, line_char)

    def count(self) -> int:
        """Возвращает число пунктов меню."""
        return len(self._menu)

    def add_callback(self, num: int, callback: tp.Callable) -> int:
        """
        Добавляет коллбэк для пункта меню. Возвращает ID коллбэка (индекс среди коллбэков пункта).

        :param num: Номер пункта.
        :param callback: Коллбэк.

        """
        if num in self._menu:
            self._menu[num].callbacks.add(callback)
            return len(self._menu) - 1

    def delete_callback(self, num: int, callback_id: int):
        if num in self._menu and len(self._menu[num].callbacks) - 1 <= callback_id:  # Последний индекс <= callback_id
            self._menu[num].callbacks.pop(callback_id)

    @property
    def menu(self) -> dict[int, 'MenuItem']:
        return self._menu

    @property
    def separators(self) -> dict[int, 'Separator']:
        return self._separators

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, description: str):
        self._description = description


@dataclass
class MenuItem:

    num: int
    name: str
    callbacks: set[tp.Callable[[], tp.Any]]


class MainMenu(Menu):
    """Главное меню."""

    # Номера элементов

    my_books, chosen, search_book, exit_ = range(1, 5)

    _menu_data = {
        my_books: MenuItem(my_books, ConsoleManager.my_books, set()),
        chosen: MenuItem(chosen, ConsoleManager.chosen, set()),
        search_book: MenuItem(search_book, ConsoleManager.search_books, set()),
        exit_: MenuItem(exit_, ConsoleManager.exit_, set())

    }

    def __init__(self):
        super().__init__(ConsoleManager.main_menu, None, self._menu_data)

    def add_callback_my_books_chosen(self, callback: tp.Callable) -> int:
        return self.add_callback(self.my_books, callback)

    def add_callback_chosen_chosen_callback(self, callback: tp.Callable) -> int:
        return self.add_callback(self.chosen, callback)

    def add_callback_search_book_chosen_callback(self, callback: tp.Callable) -> int:
        return self.add_callback(self.search_book, callback)

    def add_callback_exit_chosen_callback(self, callback: tp.Callable) -> int:
        return self.add_callback(self.exit_, callback)


class BooksMenu(Menu):
    """Меню книг пользователя."""

    # Номера пунктов меню

    to_main_menu, create_new_book, sort_books = range(1, 4)
    actions_names = [ConsoleManager.to_main_menu, ConsoleManager.create_new_book, ConsoleManager.sort_books]

    def __init__(self, sort_type: str | None = None, filter_by_genre: str | None = None, filter_by_status: str | None = None):
        self._sort_type, self._filter_by_genre, self._filter_by_status = sort_type, filter_by_genre, filter_by_status
        self._menu_data = {
            self.to_main_menu: MenuItem(self.to_main_menu, ConsoleManager.to_main_menu, set()),
            self.create_new_book: MenuItem(self.create_new_book, ConsoleManager.create_new_book, set()),
            self.sort_books: MenuItem(self.sort_books, ConsoleManager.sort_books, set())
        }
        if not self._sort_type:
            self._sort_type = ConsoleManager.no_sort
        super().__init__(ConsoleManager.books_menu, None, self._menu_data)
        self._form_description()

    def _form_description(self):
        self.description = ConsoleManager.choose_book
        if self.sort_type:
            self.description = f'{ConsoleManager.choose_book}\n{ConsoleManager.sort}: {self.sort_type}'

        if self._filter_by_status:
            self.description = (f'{self.description}\n'
                                f'{ConsoleManager.filtration_by_status}: {self._filter_by_status}')
        if self._filter_by_genre:
            self.description = (f'{self.description}\n'
                                f'{ConsoleManager.filtration_by_genre}: {self._filter_by_genre}\n')

    @property
    def sort_type(self) -> str:
        return self._sort_type

    @sort_type.setter
    def sort_type(self, sort_type: str):
        self._sort_type = sort_type
        self._form_description()

    @property
    def filter_by_genre(self) -> str:
        return self._filter_by_genre

    @filter_by_genre.setter
    def filter_by_genre(self, genre: str):
        self._filter_by_genre = genre

    @property
    def filter_by_status(self) -> str:
        return self._filter_by_genre

    @filter_by_status.setter
    def filter_by_status(self, status: str):
        self._filter_by_status = status

    def add_callback_to_main_menu_chosen(self, callback: tp.Callable) -> int:
        return self.add_callback(self.to_main_menu, callback)

    def add_callback_create_new_book(self, callback: tp.Callable) -> int:
        return self.add_callback(self.create_new_book, callback)

    def add_callback_sort_books(self, callback: tp.Callable) -> int:
        return self.add_callback(self.sort_books, callback)

    def clear(self):
        """Очищает меню от книг."""
        last_item = 3
        for item in sorted(list(self.menu.keys())):  # Ищем первый элемент, не входящий в действия меню
            if self.menu[item].name not in self.actions_names:
                last_item = item - 1

        for item in sorted(list(self.menu.keys())):  # Удаляем все элементы, номер которых больше указанного
            if item > last_item:
                self.delete_item(item)


class BookCreatingMenu(Menu):
    """
    Меню создания книги.

    :param is_creating_type: Имеет ли меню тип "Меню для создания"? Если да, то поле удаления книги не
                             отображается и привязать коллбэк к нему нельзя.

    """

    _genre: str
    _book_description: str
    _author: str
    _year: int | None
    _chosen: bool
    _status: bool

    (edit_name, edit_description, edit_author, edit_genre, edit_year, choose,
     mark_as_read, save_and_return, cancel_and_return, delete_book) = range(1, 11)
    cancel_choose, mark_as_unread = 6, 7

    def __init__(self, id_: int | None = None, is_creating_type: bool = False):
        self._menu_data = {
            self.edit_name: MenuItem(self.edit_name, ConsoleManager.edit_name, set()),
            self.edit_description: MenuItem(self.edit_description, ConsoleManager.edit_description, set()),
            self.edit_author: MenuItem(self.edit_author, ConsoleManager.edit_author, set()),
            self.edit_genre: MenuItem(self.edit_genre, ConsoleManager.edit_genre, set()),
            self.edit_year: MenuItem(self.edit_year, ConsoleManager.edit_year, set()),
            self.choose: MenuItem(self.choose, ConsoleManager.choose, set()),
            self.mark_as_read: MenuItem(self.mark_as_read, ConsoleManager.mark_as_read, set()),
            self.save_and_return: MenuItem(self.save_and_return, ConsoleManager.save_and_return, set()),
            self.cancel_and_return: MenuItem(self.cancel_and_return, ConsoleManager.cancel_and_return, set()),

    }
        if not is_creating_type:
            self._menu_data.update({self.delete_book: MenuItem(self.delete_book, ConsoleManager.delete_book, set())})
        self.id = id_
        self.is_creating_type = is_creating_type
        self._author, self._genre, self._book_description, self._year, self._status, self._chosen = '', '', '', None, False, False
        super().__init__(ConsoleManager.new_book, menu_data=self._menu_data)
        self._form_description()
        self.is_changed = False  # Есть ли изменения

    @staticmethod
    def prepare_book_description(description: str, line_length: int = 150) -> str:
        """
        Переносит по строкам текст описания книги.

        :param line_length: Длина строки.
        :param description: Описание.

        """
        book_description = list(description)
        wrapped_description = []
        for i in range(len(book_description)):
            wrapped_description.append(book_description[i])
            if i and i % line_length == 0:
                wrapped_description.append('\n')

        return ''.join(wrapped_description)

    def _form_description(self):
        """Формирует описание для меню."""
        self.description = (f"{ConsoleManager.author}: {self.author}\n{ConsoleManager.genre}: {self.genre}\n"
                            f"{ConsoleManager.description}:{'\n' if self.book_description else ''}"
                            f"{self.prepare_book_description(self.book_description)}\n"
                            f"{ConsoleManager.year}: {self.year if self.year else ''}\n"
                            f"{ConsoleManager.is_read if self.status else ConsoleManager.is_not_read}\n"
                            f"{ConsoleManager.is_chosen if self.chosen else ConsoleManager.is_not_chosen}")
        self.is_changed = True  # Описание изменяется при изменении параметров

    @property
    def chosen(self) -> bool:
        return self._chosen

    @chosen.setter
    def chosen(self, chosen: bool):  # Выбор нужного пункта меню в зависимости от того, находится ли книга в Избранном
        if chosen:
            callbacks = self._menu_data[self.choose].callbacks
            self.set_item(self.cancel_choose, ConsoleManager.cancel_choose, callbacks)
        else:
            callbacks = self._menu_data[self.cancel_choose].callbacks
            self.set_item(self.choose, ConsoleManager.choose, callbacks)
        self._chosen = chosen
        self._form_description()

    @property
    def status(self) -> bool:
        return self._status

    @status.setter
    def status(self, status: bool):
        if status:
            callbacks = self._menu_data[self.mark_as_read].callbacks
            self.set_item(self.mark_as_unread, ConsoleManager.mark_as_unread, callbacks)
        else:
            callbacks = self._menu_data[self.mark_as_unread].callbacks
            self.set_item(self.mark_as_read, ConsoleManager.mark_as_read, callbacks)
        self._status = status
        self._form_description()

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name
        self._form_description()

    @property
    def year(self) -> int | None:
        return self._year

    @year.setter
    def year(self, year: int):
        self._year = year
        self._form_description()

    @property
    def book_description(self) -> str:
        return self._book_description

    @book_description.setter
    def book_description(self, book_description: str):
        self._book_description = book_description
        self._form_description()

    @property
    def author(self) -> str:
        return self._author

    @author.setter
    def author(self, author: str):
        self._author = author
        self._form_description()

    @property
    def genre(self) -> str:
        return self._genre

    @genre.setter
    def genre(self, genre: str):
        self._genre = genre
        self._form_description()

    def add_callback_edit_name_chosen(self, callback: tp.Callable) -> int:
        return self.add_callback(self.edit_name, callback)

    def add_callback_edit_description(self, callback: tp.Callable) -> int:
        return self.add_callback(self.edit_description, callback)

    def add_callback_edit_author_chosen(self, callback: tp.Callable) -> int:
        return self.add_callback(self.edit_author, callback)

    def add_callback_edit_genre_chosen(self, callback: tp.Callable) -> int:
        return self.add_callback(self.edit_genre, callback)

    def add_callback_edit_year_chosen(self, callback: tp.Callable) -> int:
        return self.add_callback(self.edit_year, callback)

    def add_callback_change_status_chosen(self, callback: tp.Callable) -> int:
        return self.add_callback(self.mark_as_read, callback)

    def add_callback_change_chosen_chosen(self, callback: tp.Callable) -> int:
        return self.add_callback(self.choose, callback)

    def add_callback_save_and_return_chosen(self, callback: tp.Callable) -> int:
        return self.add_callback(self.save_and_return, callback)

    def add_callback_cancel_and_return_chosen(self, callback: tp.Callable) -> int:
        return self.add_callback(self.cancel_and_return, callback)

    def add_callback_delete_book_chosen(self, callback: tp.Callable) -> int:
        if self.is_creating_type:
            return 0
        return self.add_callback(self.delete_book, callback)


class ChooseMenu(Menu):

    return_to_book, add_object = range(1, 3)

    def __init__(self, name: str, description: str):
        self._menu_data = {self.return_to_book: MenuItem(self.return_to_book, ConsoleManager.return_to_book, set())}
        super().__init__(name, description, self._menu_data)

    def add_callback_return_to_book_chosen(self, callback: tp.Callable) -> int:
        return self.add_callback(self.return_to_book, callback)

    def add_callback_add_object_chosen(self, callback: tp.Callable) -> int:
        return self.add_callback(self.add_object, callback)


class Separator:
    """Разделитель для меню."""

    def __init__(self, text: str, line_char: str = '-'):
        self.text = text
        self.line_char = line_char

    def __str__(self):
        sep_line = ''.join([self.line_char for _ in range(18)])
        return f'{sep_line} {self.text} {sep_line}'


class SearchMenu(BooksMenu):
    """
    Меню для поиска книг.

    :var searching_line: Строка, введённая при поиске.
    """
    search_books = 2
    actions_names = [ConsoleManager.to_main_menu, ConsoleManager.search_books]

    def __init__(self):
        super().__init__()
        self.description = ConsoleManager.search
        self.name = ConsoleManager.title_book_search
        self.delete_item(self.sort_books)  # Удаляем пункты сортировки и добавления книги
        self.delete_item(self.create_new_book)
        self.set_item(self.search_books, ConsoleManager.search_books, set())  # Устанавливаем пункт для поиска
        self.searching_line: str | None = None

    def add_callback_search_books_chosen(self, callback: tp.Callable) -> int:
        return self.add_callback(self.search_books, callback)


if __name__ == '__main__':

    console = ConsoleManager()
    menu = Menu('Главное меню')
    new_menu = Menu('Второе меню')
    menu.set_item(1, 'Во Второе меню', [lambda: console.show_menu(new_menu)])
    new_menu.set_item(1, "В Главное меню", [lambda: console.show_menu(menu)])
    [new_menu.set_item(i, f'Пункт {i}', set()) for i in range(2, 22)]
    new_menu.set_separator(5, 'Разделитель')
    new_menu.set_separator(10, 'Разделитель')
    new_menu.set_separator(15, 'Разделитель')
    console.show_menu(menu)

