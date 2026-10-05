from datetime import datetime
import time

class BlackBox:
    # ─── Таблица предсказаний (имя таблицы — аргумент) ───

    _VALID_TABLE_RE = None  # ленивая инициализация регулярки

    # ─── Таблица предсказаний (имя таблицы — аргумент) ───

    def _validate_table_name(self, table_name: str):
        """Проверяет имя таблицы: только латиница, цифры и подчёркивания."""
        import re
        if not table_name or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name):
            raise ValueError(
                f"Недопустимое имя таблицы: {table_name!r}. "
                "Разрешены латинские буквы, цифры и подчёркивания, начинаться должно с буквы или '_'"
            )

    def _ensure_prediction_table(self, table_name: str):
        """Создаёт таблицу предсказаний, если её нет; добавляет новые столбцы,
        если таблица уже существует без них (миграция)."""
        self._validate_table_name(table_name)
        conn = self._connect()
        try:
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS "{table_name}" (
                    id                INTEGER PRIMARY KEY AUTOINCREMENT,
                    save_time         TEXT    NOT NULL,
                    actual_price      REAL,
                    predicted_price   REAL,
                    momentary_error   REAL,
                    accumulated_error REAL,
                    capital_growth    REAL
                )
            """)
            # Миграция для уже существующих таблиц: добавляем столбец, если его нет
            cursor = conn.execute(f'PRAGMA table_info("{table_name}")')
            existing_cols = {row[1] for row in cursor.fetchall()}
            if "capital_growth" not in existing_cols:
                conn.execute(f'ALTER TABLE "{table_name}" ADD COLUMN capital_growth REAL')
            conn.commit()
        finally:
            conn.close()

    def save_prediction(
            self,
            table_name: str,
            actual_price: float,
            predicted_price: float,
            capital_growth: float,
    ):
        """
        Сохраняет строку предсказания в отдельную таблицу.

        Параметры
        ---------
        table_name : str
            Имя таблицы (создаётся автоматически, если её нет).
        actual_price : float
            Цена, полученная сейчас (например, из get_current_price / get_actual_prices).
        predicted_price : float
            Предсказанная цена на следующий период (например, model["predict_next"]()).
        capital_growth : float
            Прирост капитала за текущий период. Передаётся вызывающим кодом:
            например, (price_now - price_prev) * volume, или доходность в долях:
            (price_now - price_prev) / price_prev. None сохранится как NULL.

        Возвращает id вставленной строки.
        """
        self._ensure_prediction_table(table_name)

        actual_price = float(actual_price)
        predicted_price = float(predicted_price)
        if capital_growth is not None:
            capital_growth = float(capital_growth)

        conn = self._connect()
        try:
            cursor = conn.cursor()

            # Накопленная ошибка: сумма всех предыдущих + текущая моментная
            cursor.execute(
                f'SELECT COALESCE(SUM(ABS(momentary_error)), 0.0) FROM "{table_name}"'
            )
            accumulated_prev = float(cursor.fetchone()[0])

            momentary_error = actual_price - predicted_price
            accumulated_error = accumulated_prev + abs(momentary_error)

            cursor.execute(
                f"""
                INSERT INTO "{table_name}"
                    (save_time, actual_price, predicted_price,
                     momentary_error, accumulated_error, capital_growth)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now().isoformat(),
                    actual_price,
                    predicted_price,
                    momentary_error,
                    accumulated_error,
                    capital_growth,
                ),
            )
            row_id = cursor.lastrowid
            conn.commit()
            return row_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def save_prediction(
        self,
        table_name: str,
        actual_price: float,
        predicted_price: float,
        capital_growth: float,
        momentary_error: float | None = None,
        accumulated_error: float | None = None,
    ):
        """
        Сохраняет строку предсказания в отдельную таблицу.

        Параметры
        ---------
        table_name : str
            Имя таблицы (создаётся автоматически, если её нет).
        actual_price : float
            Цена, полученная сейчас.
        predicted_price : float
            Предсказанная цена на следующий период.
        capital_growth : float | None
            Прирост капитала за текущий период.
        momentary_error : float | None, опционально
            Моментная ошибка (actual - predicted). Если передаётся, используется как есть.
            Если None — вычисляется внутри как actual_price - predicted_price.
        accumulated_error : float | None, опционально
            Накопленная ошибка. Если передаётся — пишется как есть.
            Если None — считается как сумма всех предыдущих ABS(momentary_error) + текущий ABS.

        Возвращает
        ----------
        int
            id вставленной строки.
        """
        self._ensure_prediction_table(table_name)

        # Нормализация типов
        actual_price = float(actual_price)
        predicted_price = float(predicted_price)
        if capital_growth is not None:
            capital_growth = float(capital_growth)
        if momentary_error is not None:
            momentary_error = float(momentary_error)
        if accumulated_error is not None:
            accumulated_error = float(accumulated_error)

        conn = self._connect()
        try:
            cursor = conn.cursor()

            # Если моментная ошибка не передана — считаем сами
            if momentary_error is None:
                momentary_error = actual_price - predicted_price

            # Если накопленная ошибка не передана — считаем по истории
            if accumulated_error is None:
                cursor.execute(
                    f'SELECT COALESCE(SUM(ABS(momentary_error)), 0.0) FROM "{table_name}"'
                )
                accumulated_prev = float(cursor.fetchone()[0])
                accumulated_error = accumulated_prev + abs(momentary_error)

            cursor.execute(
                f"""
                INSERT INTO "{table_name}"
                    (save_time, actual_price, predicted_price,
                     momentary_error, accumulated_error, capital_growth)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now().isoformat(),
                    actual_price,
                    predicted_price,
                    momentary_error,
                    accumulated_error,
                    capital_growth,
                ),
            )
            row_id = cursor.lastrowid
            conn.commit()
            return row_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


    def get_predictions(self, table_name: str):
        """
        Вся история предсказаний из таблицы в виде списка словарей
        (от старых к новым).
        """
        self._validate_table_name(table_name)
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"""SELECT id, save_time, actual_price, predicted_price,
                           momentary_error, accumulated_error, capital_growth
                    FROM "{table_name}" ORDER BY id"""
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": r[0],
                    "save_time": r[1],
                    "actual_price": r[2],
                    "predicted_price": r[3],
                    "momentary_error": r[4],
                    "accumulated_error": r[5],
                    "capital_growth": r[6],
                }
                for r in rows
            ]
        finally:
            conn.close()


    def replace_save_time_with_bybit_time_all(self, force: bool = False) -> dict:
        """
        Заменяет время в столбце save_time на время по часам биржи Bybit
        во ВСЕХ таблицах базы, где есть такой столбец.

        Логика: запрашивается время сервера Bybit (UTC), вычисляется суммарный
        сдвиг относительно локального времени компьютера (учитывается и дрейф
        часов, и часовой пояс — save_time писался через datetime.now().isoformat(),
        то есть в локальном времени, а биржа отдаёт UTC).

        Параметры
        ---------
        force : bool
            Если False (по умолчанию) — таблицы, уже синхронизированные ранее,
            пропускаются. Если True — сдвиг применяется ко всем таблицам.
            Осторожно: повторный сдвиг исказит время на величину нового сдвига.

        Возвращает
        ----------
        dict : {имя_таблицы: количество обновлённых строк}
        """
        import re
        import requests

        conn = self._connect()
        try:
            cursor = conn.cursor()

            # Служебная таблица: помним, какие таблицы уже синхронизированы
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS _bybit_time_sync (
                    table_name TEXT PRIMARY KEY,
                    applied_offset_seconds REAL,
                    synced_at TEXT
                )
            """)

            # ── 1. Время биржи Bybit (публичный эндпоинт, ключи не нужны) ──
            resp = requests.get("https://api.bybit.com/v5/market/time", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if data.get("retCode") != 0:
                raise RuntimeError(f"Bybit вернул ошибку: {data.get('retMsg')}")
            result = data["result"]
            bybit_ms = int(result["timeSecond"]) * 1000 + int(result.get("timeNano", 0)) // 1_000_000

            bybit_seconds = bybit_ms / 1000.0
            local_seconds = time.time()
            offset_seconds = bybit_seconds - local_seconds

            # Часовой пояс компьютера: save_time писался в локальном времени,
            # биржа — в UTC. Для Перми это +5 часов (18000 секунд).
            local_utc_offset = datetime.now().astimezone().utcoffset().total_seconds()
            total_shift_seconds = offset_seconds - local_utc_offset

            # ── 2. Все таблицы базы со столбцом save_time ──
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '\\_%' ESCAPE '\\'"
            )
            tables = [row[0] for row in cursor.fetchall()]

            tables_with_save_time = []
            for tbl in tables:
                cursor.execute(f'PRAGMA table_info("{tbl}")')
                cols = {row[1] for row in cursor.fetchall()}
                if "save_time" in cols:
                    tables_with_save_time.append(tbl)

            if not tables_with_save_time:
                conn.commit()
                return {}

            # ── 3. Сдвигаем save_time в каждой таблице ──
            results = {}
            now_iso = datetime.now().isoformat()

            for tbl in tables_with_save_time:
                # Уже синхронизирована?
                cursor.execute(
                    "SELECT 1 FROM _bybit_time_sync WHERE table_name = ?",
                    (tbl,),
                )
                if cursor.fetchone() is not None and not force:
                    results[tbl] = 0
                    continue

                cursor.execute(f'SELECT COUNT(*) FROM "{tbl}"')
                n_rows = cursor.fetchone()[0]
                if n_rows == 0:
                    results[tbl] = 0
                    continue

                cursor.execute(
                    f"""
                    UPDATE "{tbl}"
                    SET save_time = strftime(
                        '%Y-%m-%dT%H:%M:%f',
                        julianday(save_time) + (? / 86400.0)
                    )
                    WHERE save_time IS NOT NULL
                    """,
                    (total_shift_seconds,),
                )
                results[tbl] = cursor.rowcount

                # Фиксируем факт синхронизации
                cursor.execute(
                    """
                    INSERT INTO _bybit_time_sync (table_name, applied_offset_seconds, synced_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(table_name) DO UPDATE SET
                        applied_offset_seconds = excluded.applied_offset_seconds,
                        synced_at = excluded.synced_at
                    """,
                    (tbl, total_shift_seconds, now_iso),
                )

            conn.commit()
            return results
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

