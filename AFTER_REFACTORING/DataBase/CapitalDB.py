import sqlite3
from typing import List, Optional, Tuple, Any

class CapitalDB:
    def __init__(self, db_path: str):
        """
        Создаёт базу данных и таблицу, если их ещё нет.
        db_path — путь к файлу SQLite.
        """
        self.db_path = db_path
        self._create_table()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # чтобы обращаться к колонкам по имени
        return conn

    def _create_table(self) -> None:
        """Создаёт таблицу assets_capital, если её нет."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assets_capital (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_name TEXT NOT NULL,
                    capital_increment REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def insert_row(self, asset_name: str, capital_increment: float) -> int:
        """
        Вставляет одну строку: имя актива и приращение капитала.
        Возвращает id вставленной строки.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO assets_capital (asset_name, capital_increment) VALUES (?, ?)",
                (asset_name, capital_increment),
            )
            conn.commit()
            return cursor.lastrowid

    def get_all_or_by_asset(self, asset_name: Optional[str] = None) -> List[Tuple[Any, ...]]:
        """
        Если asset_name не передан — возвращает все строки таблицы.
        Если передан — возвращает строки, где asset_name совпадает (точное совпадение).
        Возвращает список кортежей (id, asset_name, capital_increment, created_at).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if asset_name is None:
                cursor.execute("SELECT * FROM assets_capital")
            else:
                # Используем параметризованный запрос для безопасности
                cursor.execute(
                    "SELECT * FROM assets_capital WHERE asset_name = ?",
                    (asset_name,)
                )
            rows = cursor.fetchall()
            # Преобразуем Row в кортежи, чтобы было проще использовать вне класса
            return [tuple(row) for row in rows]
