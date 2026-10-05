import sqlite3
from typing import List, Optional, Tuple, Any
import sqlite3
import os
from typing import List, Optional, Tuple, Any

class DataBaseManager ():
    itSelf = None

    class CapitalDB:
        def __init__(self, db_path: str):
            self.db_path = os.path.abspath(db_path)  # Превращаем в абсолютный путь
            self.dir_path = os.path.dirname(self.db_path)

            # Создаём директорию, если её нет (SQLite сам этого не делает)
            if self.dir_path and not os.path.exists(self.dir_path):
                try:
                    os.makedirs(self.dir_path, exist_ok=True)
                    print(f"[CapitalDB] Создана директория: {self.dir_path}")
                except PermissionError:
                    raise PermissionError(f"Нет прав на создание папки: {self.dir_path}") from None
                except OSError as e:
                    raise OSError(f"Ошибка создания папки: {e}") from None

            self._create_table()

        def _get_connection(self) -> sqlite3.Connection:
            # timeout помогает при работе в потоках (если другой поток держит блокировку)
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            conn.row_factory = sqlite3.Row
            # Режим WAL снижает вероятность блокировок при параллельном чтении/записи
            conn.execute("PRAGMA journal_mode=WAL;")
            return conn

        def _create_table(self) -> None:
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
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO assets_capital (asset_name, capital_increment) VALUES (?, ?)",
                    (asset_name, capital_increment),
                )
                conn.commit()
                return cursor.lastrowid

        def get_all_or_by_asset(self, asset_name: Optional[str] = None) -> List[Tuple[Any, ...]]:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if asset_name is None:
                    cursor.execute("SELECT * FROM assets_capital")
                else:
                    cursor.execute(
                        "SELECT * FROM assets_capital WHERE asset_name = ?",
                        (asset_name,)
                    )
                rows = cursor.fetchall()
                return [tuple(row) for row in rows]
