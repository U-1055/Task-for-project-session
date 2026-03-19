from tlibrary.console_manager import ConsoleManager, MainMenu, BooksMenu
from tlibrary.model import Repository, Model


# ToDo: выбор жанров из списка + возможность добавления нового жанра. То же с авторами.
# ToDo: проверить, создаются ли файлы конфига shelve DB и SQLite-БД. (Если их нет)


class Logic:
    """Класс логики приложения."""

    def __init__(self, console_manager: ConsoleManager, repo: Repository, model: Model):
        self._repo = repo
        self._model = model
        self._view = console_manager

        self._on_main_menu()

    def _on_my_books_chosen(self):
        books_menu = BooksMenu()
        books_menu.add_callback_to_main_menu_chosen(self._on_main_menu)
        books_menu.add_callback_create_new_book(self._on_create_new_book_chosen)
        books_menu.add_callback_sort_books(self._on_sort_books_chosen)
        self._view.show_menu(books_menu)

    def _on_create_new_book_chosen(self):
        pass

    def _on_sort_books_chosen(self):
        pass

    def _on_chosen_chosen(self):
        pass

    def _on_search_books_chosen(self):
        pass

    def _on_exit_chosen(self):
        line = self._view.get_data(ConsoleManager.confirm_exit).strip()
        if line == 'Y':
            exit(-1)

    def _on_main_menu(self):
        menu = MainMenu()
        menu.add_callback_my_books_chosen(self._on_my_books_chosen)
        menu.add_callback_chosen_chosen_callback(self._on_chosen_chosen)
        menu.add_callback_search_book_chosen_callback(self._on_search_books_chosen)
        menu.add_callback_exit_chosen_callback(self._on_exit_chosen)
        self._view.show_menu(menu)


