"""Точка входа в Т-библиотеку. """
from tlibrary.logic import ConsoleManager, Repository, Logic
from tlibrary.database.base_utils import launch_db, DataConst, init_db

if DataConst.default_db_pure_path.value.is_file():
    session_maker = launch_db(DataConst.default_db_path.value)
else:
    session_maker = init_db(DataConst.default_db_path.value)

try:
    logic = Logic(ConsoleManager(), Repository(session_maker))
except Exception as e:
    raise e  # ToDo: убрать raise
    print(f"Произошла непредвиденная ошибка...( Пожалуйста, перезапустите приложение.\n"
           f"Exception:\n{e.__class__.__name__}: {e}")


# ToDo: проверить - там launch_db

# ToDo: настройка сортировки + типа ПМИ и тесты
# ToDo: README с примерами использования и скринами

