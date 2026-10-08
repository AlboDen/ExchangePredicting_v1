import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path


class EraCapitalGainsDB:
    """
    База данных для учёта приращения капитала с динамическими колонками по активам.

    Имя файла: YYYY-MM-DD_HH.db в указанной папке.
    Структура таблицы capital_data:
        - exchange_time INTEGER NOT NULL (Unix timestamp)
        - settings TEXT NOT NULL (JSON)
        - total_gain REAL NOT NULL
        - capital REAL NOT NULL
        - gain_<ASSET> REAL (добавляются автоматически при первой встрече актива)
    Пример
        db = eraCapitalGainsDB("./network/DataBase/Data/capital")

        # Первая запись: 2 актива
        db.insert(
            settings={"window": 15, "method": "bestMultivariateRegression"},
            total_gain=0.0245,
            asset_gains={
                "BTCUSDT": 0.0142,
                "ETHUSDT": 0.0103,
            }
        )

        # Вторая запись: добавился SOLUSDT — колонка создастся автоматически
        db.insert(
            settings={"window": 20, "method": "bestMultivariateRegression"},
            total_gain=0.0312,
            asset_gains={
                "BTCUSDT": 0.0150,
                "ETHUSDT": 0.0080,
                "SOLUSDT": 0.0082,
            }
        )

        # Чтение всех записей
        for row in db.get_all():
            print(row["exchange_time"], row["settings"], row["total_gain"])
            # Для конкретного актива можно обратиться, например, row["gain_BTCUSDT"]

        # Список всех активов, по которым есть колонки
        print(db.get_asset_columns())  # ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']

        db = eraCapitalGainsDB("./network/DataBase/Data/capital")

        db.insert(
            settings={"window": 15, "method": "bestMultivariateRegression"},
            total_gain=0.0245,
            capital=10250.75,
            asset_gains={
                "BTCUSDT": 0.0142,
                "ETHUSDT": 0.0103,
            }
        )

        # Чтение
        for row in db.get_all():
            print(row["exchange_time"], row["capital"], row["total_gain"])
            print(row["gain_BTCUSDT"], row["gain_ETHUSDT"])


    """

    def __init__(self):
        self.folder = Path("./network/DataBase/Data/eraCapitalGains")
        self.folder.mkdir(parents=True, exist_ok=True)

        now_utc = datetime.now(timezone.utc)
        file_name = f"{now_utc:%Y-%m-%d_%H}.db"
        self.db_path = self.folder / file_name

        self._create_db_if_needed()

    @staticmethod
    def dt_to_unix(dt: datetime) -> int:
        return int(dt.replace(tzinfo=timezone.utc).timestamp())

    @staticmethod
    def unix_to_dt(ts: int) -> datetime:
        return datetime.fromtimestamp(ts, tz=timezone.utc)

    @staticmethod
    def _asset_column_name(asset: str) -> str:
        return "gain_" + "".join(c if c.isalnum() else "_" for c in asset)

    def _get_existing_columns(self, cur) -> set:
        cur.execute("PRAGMA table_info(capital_data)")
        return {row[1] for row in cur.fetchall()}

    def _ensure_columns(self, cur, asset_names: list):
        existing = self._get_existing_columns(cur)
        for asset in asset_names:
            col = self._asset_column_name(asset)
            if col not in existing:
                cur.execute(f"ALTER TABLE capital_data ADD COLUMN {col} REAL")
                existing.add(col)

    def _create_db_if_needed(self):
        if not self.db_path.exists():
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS capital_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    exchange_time INTEGER NOT NULL,
                    settings TEXT NOT NULL,
                    total_gain REAL NOT NULL,
                    capital REAL NOT NULL
                )
            """)
            cur.execute(
                "CREATE INDEX IF NOT EXISTS idx_exchange_time ON capital_data(exchange_time)"
            )
            conn.commit()
            conn.close()

    def insert(self, settings: dict, total_gain: float,
               capital: float, asset_gains: dict,
               exchange_time: datetime = None) -> int:
        """
        Универсальный метод для записи данных.

        Параметры:
            - settings: словарь настроек (сохраняется как JSON)
            - total_gain: общее приращение капитала (float)
            - capital: текущий капитал (float)
            - asset_gains: словарь частных приращений по активам {asset: gain}
            - exchange_time: время события (datetime). Если None — берётся текущее UTC.

        Возвращает: id вставленной строки.
        """
        if not isinstance(settings, dict):
            raise TypeError("settings должен быть словарем (dict)")
        if not isinstance(asset_gains, dict):
            raise TypeError("asset_gains должен быть словарем (dict)")

        if exchange_time is None:
            exchange_time = datetime.now(timezone.utc)
        ts = self.dt_to_unix(exchange_time)
        settings_json = json.dumps(settings, ensure_ascii=False)

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        asset_names = list(asset_gains.keys())
        self._ensure_columns(cur, asset_names)
        conn.commit()

        columns = ["exchange_time", "settings", "total_gain", "capital"]
        values = [ts, settings_json, total_gain, capital]

        for asset in asset_names:
            col_name = self._asset_column_name(asset)
            columns.append(col_name)
            values.append(asset_gains[asset])

        col_names_sql = ", ".join(columns)
        placeholders = ", ".join("?" * len(columns))

        cur.execute(
            f"INSERT INTO capital_data ({col_names_sql}) VALUES ({placeholders})",
            values
        )
        conn.commit()
        row_id = cur.lastrowid
        conn.close()
        return row_id

    def get_all(self):
        """Все записи. settings — dict, exchange_time — datetime."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(capital_data)")
        all_cols = [row[1] for row in cur.fetchall()]

        select_cols = ", ".join(all_cols)
        cur.execute(f"SELECT {select_cols} FROM capital_data ORDER BY exchange_time ASC")
        rows = cur.fetchall()
        conn.close()

        result = []
        for row in rows:
            row_dict = dict(zip(all_cols, row))
            row_dict["exchange_time"] = self.unix_to_dt(row_dict["exchange_time"])
            row_dict["settings"] = json.loads(row_dict["settings"])
            result.append(row_dict)
        return result

    def get_last_minutes(self, minutes: int):
        """Записи за последние N минут (UTC)."""
        now_ts = self.dt_to_unix(datetime.now(timezone.utc))
        cutoff_ts = now_ts - (minutes * 60)

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(capital_data)")
        all_cols = [row[1] for row in cur.fetchall()]
        select_cols = ", ".join(all_cols)

        cur.execute(
            f"SELECT {select_cols} FROM capital_data WHERE exchange_time >= ? ORDER BY exchange_time ASC",
            (cutoff_ts,)
        )
        rows = cur.fetchall()
        conn.close()

        result = []
        for row in rows:
            row_dict = dict(zip(all_cols, row))
            row_dict["exchange_time"] = self.unix_to_dt(row_dict["exchange_time"])
            row_dict["settings"] = json.loads(row_dict["settings"])
            result.append(row_dict)
        return result

    def get_asset_columns(self) -> list:
        """Список названий активов, для которых есть колонки (без префикса gain_)."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(capital_data)")
        cols = [row[1] for row in cur.fetchall()]
        conn.close()
        return [c[5:] for c in cols if c.startswith("gain_")]
