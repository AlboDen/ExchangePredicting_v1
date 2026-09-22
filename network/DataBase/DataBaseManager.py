import sqlite3
import os
from datetime import datetime
import threading
from datetime import datetime

class DataBaseManager:
    class OrderbookDatabase:
        # ... (все ваши существующие методы) ...

        def fill_database_in_background(
                self,
                raw_asks_prices,
                raw_asks_sizes,
                raw_bids_prices,
                raw_bids_sizes,
                wall_asks_points=None,
                wall_bids_points=None,
                static_params=None,
                dynamic_1_params=None,
                dynamic_5_params=None,
                dynamic_10_params=None,
                weights=None,
                on_success=None,
                on_error=None
        ):
            """
            Запускает заполнение БД в отдельном потоке.
            Если БД или таблицы не существует — создаёт их автоматически.

            Параметры:
                raw_asks_prices, raw_asks_sizes — отдельные списки цен и размеров для asks
                raw_bids_prices, raw_bids_sizes — отдельные списки цен и размеров для bids
                wall_asks_points, wall_bids_points — списки кортежей [(price, size), ...]
                static_params — dict {название: значение}
                dynamic_*_params — dicts для 1/5/10 циклов
                weights — dict {param_name: weight}
                on_success(request_id) — callback, вызывается в главном потоке при успехе
                on_error(exc) — callback при ошибке
            """

            def worker():
                conn = None
                try:
                    # Создаём папку, если её не существует
                    db_dir = os.path.dirname(self.db_path)
                    if db_dir and not os.path.exists(db_dir):
                        os.makedirs(db_dir)

                    # sqlite3.connect автоматически создаст файл, если его нет
                    conn = sqlite3.connect(self.db_path, timeout=10.0)
                    conn.execute("PRAGMA foreign_keys = ON")

                    # Проверяем, есть ли центральная таблица requests.
                    # Если нет — создаём все таблицы с нуля.
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name='requests'"
                    )
                    if cursor.fetchone() is None:
                        # Создаём все таблицы
                        for tbl in self.POINT_TABLE_NAMES.values():
                            self._create_point_table(cursor, tbl)
                        self._create_static_params_table(cursor)
                        for tbl in self.DYNAMIC_TABLE_NAMES.values():
                            self._create_dynamic_params_table(cursor, tbl)
                        self._create_weights_table(cursor)
                        self._create_central_table(cursor)
                        conn.commit()

                    # Сшиваем цены и размеры в кортежи
                    raw_asks_points = list(zip(raw_asks_prices, raw_asks_sizes))
                    raw_bids_points = list(zip(raw_bids_prices, raw_bids_sizes))

                    # Вставляем точки
                    raw_asks_id = self._insert_points_internal(conn, "raw_asks", raw_asks_points)
                    raw_bids_id = self._insert_points_internal(conn, "raw_bids", raw_bids_points)

                    # Стены (если переданы)
                    wall_asks_id = (
                        self._insert_points_internal(conn, "wall_asks", wall_asks_points)
                        if wall_asks_points else None
                    )
                    wall_bids_id = (
                        self._insert_points_internal(conn, "wall_bids", wall_bids_points)
                        if wall_bids_points else None
                    )

                    # Статические параметры
                    static_params_id = (
                        self._insert_static_params_internal(conn, static_params)
                        if static_params else None
                    )

                    # Динамические параметры
                    dynamic_1_id = (
                        self._insert_dynamic_params_internal(conn, 1, dynamic_1_params)
                        if dynamic_1_params else None
                    )
                    dynamic_5_id = (
                        self._insert_dynamic_params_internal(conn, 5, dynamic_5_params)
                        if dynamic_5_params else None
                    )
                    dynamic_10_id = (
                        self._insert_dynamic_params_internal(conn, 10, dynamic_10_params)
                        if dynamic_10_params else None
                    )

                    # Веса
                    weights_id = (
                        self._insert_weights_internal(conn, weights)
                        if weights else None
                    )

                    # Центральная запись
                    request_time = datetime.now().isoformat()
                    cursor = conn.cursor()
                    cursor.execute(
                        """INSERT INTO requests (
                            request_time, raw_asks_id, raw_bids_id,
                            wall_asks_id, wall_bids_id,
                            static_params_id,
                            dynamic_params_1cycle_id,
                            dynamic_params_5cycles_id,
                            dynamic_params_10cycles_id,
                            weights_id
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            request_time, raw_asks_id, raw_bids_id,
                            wall_asks_id, wall_bids_id,
                            static_params_id,
                            dynamic_1_id, dynamic_5_id, dynamic_10_id,
                            weights_id,
                        ),
                    )
                    conn.commit()
                    request_id = cursor.lastrowid

                    if on_success is not None:
                        self._root.after(0, lambda: on_success(request_id))

                except Exception as e:
                    if on_error is not None:
                        self._root.after(0, lambda: on_error(e))
                finally:
                    if conn:
                        conn.close()

            t = threading.Thread(target=worker, daemon=True)
            t.start()


