"""Консольное приложение "Т-библиотека" """

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

    separator = '-------------------------------------------------------'
    menu_padding = '\n\n\n\n\n'

    # Пункты меню

    my_books = "Мои книги"
    chosen = 'Избранное'
    search_book = 'Найти книгу'
    exit_ = 'Выйти из приложения'
    create_new_book = 'Новая книга'
    to_main_menu = 'В Главное меню'
    sort_books = 'Сортировать книги'

    # Описания меню

    choose_book = 'Выберите книгу'

    # Прочие надписи
    confirm_exit = 'Вы уверены, что хотите выйти? ([Y] - ДА, любая другая клавиша - НЕТ): '

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
        for item_ in menu.menu:
            print(f'{item_}. {menu.menu[item_].name}')
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
        self.name = name
        self._description = description

    def set_item(self, num: int, name: str, callbacks: list[tp.Callable]):
        self._menu[num] = MenuItem(num, name, callbacks)

    def add_callback(self, num: int, callback: tp.Callable) -> int:
        """
        Добавляет коллбэк для пункта меню. Возвращает ID коллбэка (индекс среди коллбэков пункта).

        :param num: Номер пункта.
        :param callback: Коллбэк.

        """
        if num in self._menu:
            self._menu[num].callbacks.append(callback)
            return len(self._menu) - 1

    def delete_callback(self, num: int, callback_id: int):
        if num in self._menu and len(self._menu[num].callbacks) - 1 <= callback_id:  # Последний индекс <= callback_id
            self._menu[num].callbacks.pop(callback_id)

    @property
    def menu(self) -> dict[int, 'MenuItem']:
        return self._menu

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
    callbacks: list[tp.Callable[[], tp.Any]]


class MainMenu(Menu):
    """Главное меню."""

    # Номера элементов

    my_books, chosen, search_book, exit_ = range(1, 5)

    _menu_data = {
        my_books: MenuItem(my_books, ConsoleManager.my_books, []),
        chosen: MenuItem(chosen, ConsoleManager.chosen, []),
        search_book: MenuItem(search_book, ConsoleManager.search_book, []),
        exit_: MenuItem(exit_, ConsoleManager.exit_, [])

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

    _menu_data = {
        to_main_menu: MenuItem(to_main_menu, ConsoleManager.to_main_menu, []),
        create_new_book: MenuItem(create_new_book, ConsoleManager.create_new_book, []),
        sort_books: MenuItem(sort_books, ConsoleManager.sort_books, [])
    }

    def __init__(self):
        super().__init__(ConsoleManager.books_menu, ConsoleManager.choose_book, self._menu_data)

    def add_callback_to_main_menu_chosen(self, callback: tp.Callable) -> int:
        return self.add_callback(self.to_main_menu, callback)

    def add_callback_create_new_book(self, callback: tp.Callable) -> int:
        return self.add_callback(self.create_new_book, callback)

    def add_callback_sort_books(self, callback: tp.Callable) -> int:
        return self.add_callback(self.sort_books, callback)


if __name__ == '__main__':

    console = ConsoleManager()
    menu = Menu('Главное меню')
    new_menu = Menu('Второе меню')
    menu.set_item(1, 'Во Второе меню', [lambda: console.show_menu(new_menu)])
    new_menu.set_item(1, "В Главное меню", [lambda: console.show_menu(menu)])
    console.show_menu(menu)
