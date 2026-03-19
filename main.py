"""Точка входа в Т-библиотеку. """
from pathlib import Path
from tlibrary.logic import ConsoleManager, Repository, Logic, Model
from tlibrary.database.base_utils import init_db, launch_db, DataConst

try:
    session_maker = launch_db(DataConst.default_db_path.value)
except Exception as e:  # ToDo: детализировать исключение
    session_maker = init_db(DataConst.default_db_path.value)

logic = Logic(ConsoleManager(), Repository(session_maker), Model(Path('tlibrary', 'database', 'config')))
