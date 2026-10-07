import sqlite3
import os
from datetime import datetime, timezone
from pathlib import Path

class CapitalGainDB:
    """
    Менеджер БД прироста капитала.
    Хранит exchange_time как Unix timestamp (INTEGER) — удобно для расчётов и фильтрации.
    Создаёт файл вида capitalGainDB_YYYY-MM-DD_HH.db, если его ещё нет.
    """

    DB_FOLDER = Path("./network/DataBase/Data/capitalGains")

    def __init__(self):
        # Время биржи (UTC) для имени файла
        self.exchange_dt = datetime.now(timezone.utc)

        file_name = f"{self.exchange_dt:%Y-%m-%d_%H}.db"
        self.DB_FOLDER.mkdir(exist_ok=True)
        self.db_path = self.DB_FOLDER / file_name

        self._create_db_if_needed()

    def _create_db_if_needed(self):
        """Создаёт БД и таблицу, если файла ещё нет."""
        if not self.db_path.exists():
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS capital_gain (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asset_name TEXT NOT NULL,
                    method TEXT NOT NULL,
                    capital_gain REAL NOT NULL,
                    exchange_time INTEGER NOT NULL  -- Unix timestamp (секунды)
                )
            """)
            # Индекс по времени — полезно для выборки «за последние X минут»
            cur.execute("CREATE INDEX IF NOT EXISTS idx_exchange_time ON capital_gain(exchange_time)")
            conn.commit()
            conn.close()

    @staticmethod
    def dt_to_unix(dt: datetime) -> int:
        """Конвертирует datetime (в UTC) в Unix timestamp (int)."""
        return int(dt.replace(tzinfo=timezone.utc).timestamp())

    @staticmethod
    def unix_to_dt(ts: int) -> datetime:
        """Конвертирует Unix timestamp в datetime (UTC)."""
        return datetime.fromtimestamp(ts, tz=timezone.utc)

    def insert(self, asset_name: str, method: str, capital_gain: float,
               exchange_time: datetime = None):
        """
        Вставка записи.
        exchange_time: если не передан — берётся текущее биржевое время (UTC).
        Если у тебя есть время из API Bybit (мс), передай его как datetime.
        """
        try:
            if exchange_time is None:
                exchange_time = datetime.now(timezone.utc)

            ts = self.dt_to_unix(exchange_time)

            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute(
        """
                INSERT INTO capital_gain (asset_name, method, capital_gain, exchange_time)
                VALUES (?, ?, ?, ?)
            """, (asset_name, method, capital_gain, ts))
            conn.commit()
            conn.close()
        except sqlite3.OperationalError:
            print("RIZE: sqlite3.OperationalError")

    def get_all(self):
        """Возвращает все записи с конвертацией времени в datetime."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT asset_name, method, capital_gain, exchange_time FROM capital_gain")
        rows = cur.fetchall()
        conn.close()
        # Конвертируем timestamp в datetime для удобства (можно сразу для Treeview)
        return [(a, m, g, self.unix_to_dt(t)) for a, m, g, t in rows]

    def get_by_asset(self, asset_name: str):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT asset_name, method, capital_gain, exchange_time
            FROM capital_gain WHERE asset_name = ?
        """, (asset_name,))
        rows = cur.fetchall()
        conn.close()
        return [(a, m, g, self.unix_to_dt(t)) for a, m, g, t in rows]

    def get_last_minutes(self, minutes: int):
        """Выборка записей за последние N минут (удобно для графиков/регрессий)."""
        now_ts = self.dt_to_unix(datetime.now(timezone.utc))
        cutoff_ts = now_ts - (minutes * 60)

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT asset_name, method, capital_gain, exchange_time
            FROM capital_gain
            WHERE exchange_time >= ?
            ORDER BY exchange_time ASC
        """, (cutoff_ts,))
        rows = cur.fetchall()
        conn.close()
        return [(a, m, g, self.unix_to_dt(t)) for a, m, g, t in rows]
