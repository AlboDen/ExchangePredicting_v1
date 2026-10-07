import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path


class MethodDataDB:
    """
    TO COLLECT CHANGING OF METHODS PARAMS

    Менеджер БД данных методов.
    Создаёт файл вида YYYY-MM-DD_HH.db (дата и час биржи) в папке
    ./network/DataBase/Data/methodsData/{asset}, если такого файла ещё нет.

    Столбцы:
        exchange_time  — время по бирже формирования лучшего метода (Unix timestamp)
        parameters     — параметры метода (хранятся как JSON-список)
        method_name    — название метода
        capital_gain   — прирост капитала
        capital_loss   — потеря капитала
        error_count    — количество ошибок

    Логика ввода:
        add_method(...)   — передаются только первые 3 столбца → создаётся новая строка
        fill_results(...) — передаются только последние 3 столбца → заполняется предпоследняя строка
    Example using:
        DataBaseManager.itSelf.MethodsDataDB["BTCUSDT"].add_method(
            # exchange_time, parameters, method_name
            parameters=[14, 5],
            method_name="fff_meth"
        )
        DataBaseManager.itSelf.MethodsDataDB["BTCUSDT"].add_method(
            # exchange_time, parameters, method_name
            parameters=[14, 5],
            method_name="fff_meth"
        )
        DataBaseManager.itSelf.MethodsDataDB["BTCUSDT"].fill_results(
            #     self, capital_gain: float, capital_loss: float,
            #                      error_count: int
            capital_gain=12,
            capital_loss=4,
            error_count=-6
        )
        DataBaseManager.itSelf.MethodsDataDB["BTCUSDT"].fill_results(
            #     self, capital_gain: float, capital_loss: float,
            #                      error_count: int
            capital_gain=12,
            capital_loss=4,
            error_count=-8
        )
    """

    def __init__(self, asset: str):
        """
        asset — название актива (например, "BTCUSDT").
        Файл БД сохраняется в ./network/DataBase/Data/methodsData/{asset}/
        """
        self.folder = Path(f"./network/DataBase/Data/methodsData/{asset}")
        self.folder.mkdir(parents=True, exist_ok=True)

        # Время биржи (UTC) для имени файла
        self.exchange_dt = datetime.now(timezone.utc)
        file_name = f"{self.exchange_dt:%Y-%m-%d_%H}.db"
        self.db_path = self.folder / file_name

        self._create_db_if_needed()

    def _create_db_if_needed(self):
        """Создаёт БД и таблицу, если файла ещё нет."""
        if not self.db_path.exists():
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS method_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    exchange_time INTEGER NOT NULL,   -- время по бирже (Unix timestamp)
                    parameters TEXT NOT NULL,         -- параметры метода (JSON-список)
                    method_name TEXT NOT NULL,        -- название метода
                    capital_gain REAL,                -- прирост капитала (заполняется позже)
                    capital_loss REAL,                -- потеря капитала (заполняется позже)
                    error_count INTEGER               -- количество ошибок (заполняется позже)
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_exchange_time ON method_data(exchange_time)")
            conn.commit()
            conn.close()

    # ---------- Конвертация времени ----------

    @staticmethod
    def dt_to_unix(dt: datetime) -> int:
        """datetime (UTC) → Unix timestamp (секунды)."""
        return int(dt.replace(tzinfo=timezone.utc).timestamp())

    @staticmethod
    def unix_to_dt(ts: int) -> datetime:
        """Unix timestamp → datetime (UTC)."""
        return datetime.fromtimestamp(ts, tz=timezone.utc)

    # ---------- Сериализация параметров ----------

    @staticmethod
    def params_to_json(parameters: list) -> str:
        """Список параметров → JSON-строка для хранения в БД."""
        return json.dumps(parameters, ensure_ascii=False)

    @staticmethod
    def json_to_params(params_json: str) -> list:
        """JSON-строка из БД → список параметров."""
        return json.loads(params_json)

    # ---------- Ввод первых трёх столбцов: новая строка ----------

    def add_method(self, parameters: list, method_name: str):
        """
        Создаёт НОВУЮ строку с первыми тремя столбцами:
        время по бирже, параметры (список), название метода.
        Последние три столбца остаются NULL до вызова fill_results.

        parameters — список любых значений, например:
            [15, 0.02, "linear"] или
            [1709800000, [0.1, 0.2], {"window": 15}]
        """
        if not isinstance(parameters, list):
            raise TypeError("parameters должен быть списком (list)")

        # if exchange_time is None:
        exchange_time = datetime.now(timezone.utc)
        ts = int(self.dt_to_unix(exchange_time))

        params_json = self.params_to_json(parameters)

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO method_data (exchange_time, parameters, method_name)
            VALUES (?, ?, ?)
        """, (ts, params_json, method_name))
        conn.commit()
        row_id = cur.lastrowid
        conn.close()
        return row_id

    # ---------- Ввод последних трёх столбцов: предпоследняя строка ----------

    def fill_results(self, capital_gain: float, capital_loss: float,
                     error_count: int):
        """
        Заполняет последние три столбца (прирост, потеря, количество ошибок)
        у ПОСЛЕДНЕЙ строки таблицы.

        Если таблица пуста — вызывает ошибку.
        """
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM method_data")
        count = cur.fetchone()[0]

        if count == 0:
            conn.close()
            raise ValueError("Таблица пуста: сначала вызовите add_method, чтобы создать строку.")

        # Последняя строка = максимальный id
        cur.execute("""
            SELECT id FROM method_data
            ORDER BY id DESC
            LIMIT 1
        """)
        target_id = cur.fetchone()[0]

        cur.execute("""
            UPDATE method_data
            SET capital_gain = ?, capital_loss = ?, error_count = ?
            WHERE id = ?
        """, (capital_gain, capital_loss, error_count, target_id))
        conn.commit()
        conn.close()
        return target_id

    # ---------- Чтение ----------

    def get_all(self):
        """Все записи. parameters возвращаются как список."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT exchange_time, parameters, method_name,
                   capital_gain, capital_loss, error_count
            FROM method_data
            ORDER BY exchange_time ASC
        """)
        rows = cur.fetchall()
        conn.close()
        return [
            (self.unix_to_dt(t), self.json_to_params(p), m, g, l, e)
            for t, p, m, g, l, e in rows
        ]

    def get_incomplete(self):
        """Строки, у которых результаты ещё не заполнены (последние 3 столбца — NULL)."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT exchange_time, parameters, method_name
            FROM method_data
            WHERE capital_gain IS NULL AND capital_loss IS NULL AND error_count IS NULL
            ORDER BY exchange_time ASC
        """)
        rows = cur.fetchall()
        conn.close()
        return [(self.unix_to_dt(t), self.json_to_params(p), m) for t, p, m in rows]

    def get_by_method(self, method_name: str):
        """Записи по конкретному методу. parameters возвращаются как список."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            SELECT exchange_time, parameters, method_name,
                   capital_gain, capital_loss, error_count
            FROM method_data
            WHERE method_name = ?
            ORDER BY exchange_time ASC
        """, (method_name,))
        rows = cur.fetchall()
        conn.close()
        return [
            (self.unix_to_dt(t), self.json_to_params(p), m, g, l, e)
            for t, p, m, g, l, e in rows
        ]
