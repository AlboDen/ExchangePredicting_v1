"""
DataBaseManager — менеджер локальной базы данных SQLite.

Схема БД:
    requests (центральная таблица)
      ├── id               — порядковый номер запроса (AUTOINCREMENT)
      ├── request_time     — время обращения
      ├── asks_count       — количество точек asks
      ├── bids_count       — количество точек bids
      ├── asks_prices      — список цен asks   (JSON, float[])
      ├── asks_sizes       — список объёмов asks (JSON, float[])
      ├── bids_prices      — список цен bids    (JSON, float[])
      ├── bids_sizes       — список объёмов bids (JSON, float[])
      ├── static_id        → ссылка на static_params
      └── dynamic_id       → ссылка на dynamic_params

    static_params
      ├── id                              — первичный ключ
      ├── spread                          — спрэд (разница между лучшими ценами спроса и предложения)
      ├── regression_area_ratio           — отношение площадей под линией регрессии (bids/asks)
      ├── rectangle_area_ratio            — отношение площадей прямоугольника (bids/asks)
      ├── regression_coeff_ratio          — отношение коэффициентов регрессии (наклонов линий) для bids/asks
      ├── points_above_regression_ratio   — отношение количества точек над линией регрессии к общему числу точек
      ├── asks_third1_count               — количество точек в 1‑й трети прямоугольника по оси цены (asks)
      ├── asks_third2_count               — количество точек во 2‑й трети прямоугольника (asks)
      ├── asks_third3_count               — количество точек в 3‑й трети прямоугольника (asks)
      ├── bids_third1_count               — количество точек в 1‑й трети прямоугольника по оси цены (bids)
      ├── bids_third2_count               — количество точек во 2‑й трети прямоугольника (bids)
      └── bids_third3_count               — количество точек в 3‑й трети прямоугольника (bids)

    dynamic_params (связующая таблица)
      ├── id
      ├── short_term_id  → dynamic_params_SHORT_term
      ├── medium_term_id → dynamic_params_MEDIUM_term
      └── long_term_id   → dynamic_params_LONG_term

    dynamic_params_SHORT_term / MEDIUM_term / LONG_term (одинаковая структура)
      ├── все поля static_params +
      ├── equilibrium_vector_magnitude_growth_ratio  — пропорция увеличения модуля вектора изменения равновесия
      ├── equilibrium_price_growth_ratio             — пропорция увеличения равновесной цены
      ├── equilibrium_demand_growth_ratio            — пропорция увеличения равновесного спроса
      ├── open_price_growth_ratio                    — пропорция увеличения цены открытия
      ├── close_price_growth_ratio                   — пропорция увеличения цены закрытия
      ├── max_price_growth_ratio                     — пропорция увеличения максимальной цены
      └── min_price_growth_ratio                     — пропорция увеличения минимальной цены
"""

import sqlite3
import os
import json
from datetime import datetime


class DataBaseManager:
    def __init__(self, db_path="orderbook.db"):
        self.db_path = db_path

        db_dir = os.path.dirname(os.path.abspath(db_path))
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        self._create_tables()

    # ─── Внутренние методы ───

    def _connect(self):
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _create_tables(self):
        conn = self._connect()
        try:
            cursor = conn.cursor()

            # ── Term-таблицы динамических параметров (одинаковая структура) ──
            for tbl in (
                "dynamic_params_SHORT_term",
                "dynamic_params_MEDIUM_term",
                "dynamic_params_LONG_term",
            ):
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS "{tbl}" (
                        id                                  INTEGER PRIMARY KEY AUTOINCREMENT,
                        spread                              REAL,
                        regression_area_ratio               REAL,
                        rectangle_area_ratio                REAL,
                        regression_coeff_ratio              REAL,
                        points_above_regression_ratio       REAL,
                        asks_third1_count                   INTEGER,
                        asks_third2_count                   INTEGER,
                        asks_third3_count                   INTEGER,
                        bids_third1_count                   INTEGER,
                        bids_third2_count                   INTEGER,
                        bids_third3_count                   INTEGER,
                        equilibrium_vector_magnitude_growth_ratio  REAL,
                        equilibrium_price_growth_ratio            REAL,
                        equilibrium_demand_growth_ratio          REAL,
                        open_price_growth_ratio                   REAL,
                        close_price_growth_ratio                  REAL,
                        max_price_growth_ratio                    REAL,
                        min_price_growth_ratio                    REAL
                    )
                """)

            # ── Таблица статических параметров ──
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS static_params (
                    id                              INTEGER PRIMARY KEY AUTOINCREMENT,
                    spread                          REAL,
                    regression_area_ratio           REAL,
                    rectangle_area_ratio            REAL,
                    regression_coeff_ratio          REAL,
                    points_above_regression_ratio   REAL,
                    asks_third1_count               INTEGER,
                    asks_third2_count               INTEGER,
                    asks_third3_count               INTEGER,
                    bids_third1_count               INTEGER,
                    bids_third2_count               INTEGER,
                    bids_third3_count               INTEGER
                )
            """)

            # ── Связующая таблица динамических параметров ──
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS dynamic_params (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    short_term_id  INTEGER,
                    medium_term_id INTEGER,
                    long_term_id   INTEGER,
                    FOREIGN KEY (short_term_id)  REFERENCES dynamic_params_SHORT_term(id),
                    FOREIGN KEY (medium_term_id) REFERENCES dynamic_params_MEDIUM_term(id),
                    FOREIGN KEY (long_term_id)   REFERENCES dynamic_params_LONG_term(id)
                )
            """)

            # ── Центральная таблица ──
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_time  TEXT    NOT NULL,
                    asks_count    INTEGER,
                    bids_count    INTEGER,
                    asks_prices   TEXT,
                    asks_sizes    TEXT,
                    bids_prices   TEXT,
                    bids_sizes    TEXT,
                    static_id     INTEGER,
                    dynamic_id    INTEGER,
                    FOREIGN KEY (static_id)  REFERENCES static_params(id),
                    FOREIGN KEY (dynamic_id) REFERENCES dynamic_params(id)
                )
            """)

            conn.commit()
        finally:
            conn.close()

    # ─── Вспомогательные методы ───

    # Колонки, общие для static_params и term-таблиц
    _COMMON_COLUMNS = [
        "spread",
        "regression_area_ratio",
        "rectangle_area_ratio",
        "regression_coeff_ratio",
        "points_above_regression_ratio",
        "asks_third1_count",
        "asks_third2_count",
        "asks_third3_count",
        "bids_third1_count",
        "bids_third2_count",
        "bids_third3_count",
    ]

    # Дополнительные колонки только для term-таблиц
    _EXTRA_TERM_COLUMNS = [
        "equilibrium_vector_magnitude_growth_ratio",
        "equilibrium_price_growth_ratio",
        "equilibrium_demand_growth_ratio",
        "open_price_growth_ratio",
        "close_price_growth_ratio",
        "max_price_growth_ratio",
        "min_price_growth_ratio",
    ]

    def _insert_row(self, cursor, table_name, data):
        """Универсальная вставка словаря в таблицу. Возвращает lastrowid."""
        cols = list(data.keys())
        vals = list(data.values())
        placeholders = ", ".join(["?"] * len(vals))
        cols_quoted = ", ".join(f'"{c}"' for c in cols)
        cursor.execute(
            f'INSERT INTO "{table_name}" ({cols_quoted}) VALUES ({placeholders})',
            vals,
        )
        return cursor.lastrowid

    def _build_term_dict(self, params):
        """
        Принимает dict и оставляет только ключи,
        которые валидны для term-таблиц (отбрасывает None).
        """
        valid_keys = self._COMMON_COLUMNS + self._EXTRA_TERM_COLUMNS
        return {k: v for k, v in params.items() if k in valid_keys and v is not None}

    # ─── Публичный метод вставки ───

    def insert_request(
        self,
        asks_prices,
        asks_volumes,
        bids_prices,
        bids_volumes,
        spread=None,
        regression_area_ratio=None,
        rectangle_area_ratio=None,
        regression_coeff_ratio=None,
        points_above_regression_ratio=None,
        asks_third1_count=None,
        asks_third2_count=None,
        asks_third3_count=None,
        bids_third1_count=None,
        bids_third2_count=None,
        bids_third3_count=None,
        short_term_params=None,
        medium_term_params=None,
        long_term_params=None,
    ):
        """
        Заполняет БД: вставляет статические и динамические параметры,
        связывает всё через центральную таблицу.
        Потокобезопасен.

        Параметры:
            asks_prices, asks_volumes, bids_prices, bids_volumes — list[float]
            spread, regression_*, rectangle_*, points_above_*,
            asks_third*, bids_third* — статические параметры

            short_term_params  — dict | None для dynamic_params_SHORT_term
            medium_term_params — dict | None для dynamic_params_MEDIUM_term
            long_term_params   — dict | None для dynamic_params_LONG_term

            Ключи term-словарей: spread, regression_area_ratio,
            rectangle_area_ratio, regression_coeff_ratio,
            points_above_regression_ratio,
            asks_third1/2/3_count, bids_third1/2/3_count,
            equilibrium_vector_magnitude_growth_ratio,
            equilibrium_price_growth_ratio,
            equilibrium_demand_growth_ratio,
            open_price_growth_ratio,
            close_price_growth_ratio,
            max_price_growth_ratio,
            min_price_growth_ratio

        Возвращает: request_id.
        """
        conn = self._connect()
        try:
            cursor = conn.cursor()

            # ── Статические параметры ──
            static_data = {
                k: v for k, v in {
                    "spread": spread,
                    "regression_area_ratio": regression_area_ratio,
                    "rectangle_area_ratio": rectangle_area_ratio,
                    "regression_coeff_ratio": regression_coeff_ratio,
                    "points_above_regression_ratio": points_above_regression_ratio,
                    "asks_third1_count": asks_third1_count,
                    "asks_third2_count": asks_third2_count,
                    "asks_third3_count": asks_third3_count,
                    "bids_third1_count": bids_third1_count,
                    "bids_third2_count": bids_third2_count,
                    "bids_third3_count": bids_third3_count,
                }.items() if v is not None
            }

            static_id = self._insert_row(cursor, "static_params", static_data) if static_data else None

            # ── Динамические term-таблицы ──
            short_term_id = None
            medium_term_id = None
            long_term_id = None

            if short_term_params:
                data = self._build_term_dict(short_term_params)
                if data:
                    short_term_id = self._insert_row(cursor, "dynamic_params_SHORT_term", data)

            if medium_term_params:
                data = self._build_term_dict(medium_term_params)
                if data:
                    medium_term_id = self._insert_row(cursor, "dynamic_params_MEDIUM_term", data)

            if long_term_params:
                data = self._build_term_dict(long_term_params)
                if data:
                    long_term_id = self._insert_row(cursor, "dynamic_params_LONG_term", data)

            # ── Связующая таблица dynamic_params ──
            dynamic_id = None
            if any([short_term_id, medium_term_id, long_term_id]):
                cursor.execute(
                    """INSERT INTO dynamic_params
                       (short_term_id, medium_term_id, long_term_id)
                       VALUES (?, ?, ?)""",
                    (short_term_id, medium_term_id, long_term_id),
                )
                dynamic_id = cursor.lastrowid

            # ── Центральная таблица ──
            request_time = datetime.now().isoformat()
            cursor.execute(
                """INSERT INTO requests
                   (request_time, asks_count, bids_count,
                    asks_prices, asks_sizes, bids_prices, bids_sizes,
                    static_id, dynamic_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    request_time,
                    len(asks_prices),
                    len(bids_prices),
                    json.dumps(asks_prices, ensure_ascii=False),
                    json.dumps(asks_volumes, ensure_ascii=False),
                    json.dumps(bids_prices, ensure_ascii=False),
                    json.dumps(bids_volumes, ensure_ascii=False),
                    static_id,
                    dynamic_id,
                ),
            )
            request_id = cursor.lastrowid

            conn.commit()
            return request_id

        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ─── Методы чтения ───

    def get_all_requests(self):
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, request_time, asks_count, bids_count,
                          static_id, dynamic_id
                   FROM requests ORDER BY id"""
            )
            return cursor.fetchall()
        finally:
            conn.close()

    def get_request_by_id(self, request_id):
        """Полная запись: requests + static_params + dynamic_params (со ссылками).
        Списки цен/объёмов распаковываются из JSON в list[float]."""
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT r.id, r.request_time, r.asks_count, r.bids_count,
                       r.asks_prices, r.asks_sizes,
                       r.bids_prices, r.bids_sizes,
                       s.spread,
                       s.regression_area_ratio, s.rectangle_area_ratio,
                       s.regression_coeff_ratio, s.points_above_regression_ratio,
                       s.asks_third1_count, s.asks_third2_count, s.asks_third3_count,
                       s.bids_third1_count, s.bids_third2_count, s.bids_third3_count,
                       d.short_term_id, d.medium_term_id, d.long_term_id
                FROM requests r
                LEFT JOIN static_params  s ON r.static_id  = s.id
                LEFT JOIN dynamic_params d ON r.dynamic_id = d.id
                WHERE r.id = ?
                """,
                (request_id,),
            )
            row = cursor.fetchone()
            if row:
                row = list(row)
                for i in (4, 5, 6, 7):
                    if row[i] is not None:
                        row[i] = json.loads(row[i])
            return row
        finally:
            conn.close()

    def get_term_params(self, term_table, term_id):
        """
        Возвращает строку из term-таблицы по id.

        term_table: 'dynamic_params_SHORT_term' |
                     'dynamic_params_MEDIUM_term' |
                     'dynamic_params_LONG_term'
        """
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f'SELECT * FROM "{term_table}" WHERE id = ?',
                (term_id,),
            )
            return cursor.fetchone()
        finally:
            conn.close()

