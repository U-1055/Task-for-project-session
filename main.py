"""Точка входа в Т-библиотеку. """
from pathlib import Path
from tlibrary.logic import ConsoleManager, Repository, Logic, Model
from tlibrary.database.base_utils import launch_db, DataConst, init_db

if DataConst.default_db_pure_path.value.is_file():
    session_maker = launch_db(DataConst.default_db_path.value)
else:
    session_maker = init_db(DataConst.default_db_path.value)

try:
    logic = Logic(ConsoleManager(), Repository(session_maker), Model(Path('tlibrary', 'database', 'config')))
except Exception as e:
    print(f"Произошла непредвиденная ошибка...( Пожалуйста, перезапустите приложение.\n"
          f"Exception:\n{e.__class__.__name__}: {e}")

# ToDo: протестировать валидацию
# ToDo: проверить - там launch_db

# ToDo: настройка сортировки + типа ПМИ и тесты
