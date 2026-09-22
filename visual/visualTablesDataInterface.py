import threading
import queue
from network.DataBase.DataBaseManager import DataBaseManager


class VisualTablesInterface:
    itSelf = None

    STATIC_VALUE_COLS = ("bids", "asks")
    DYNAMIC_CYCLES = ("1 цикл", "5 цикл.", "10 цикл.")
    DYNAMIC_SIDES = ("bids", "asks")
    _COLOR_TAG_PREFIX = "_fg_"

    def __init__(self, static_tree, dynamic_tree):
        self.static_tree = static_tree
        self.dynamic_tree = dynamic_tree
        self._static_index = self._build_index_impl(static_tree)
        self._dynamic_index = self._build_index_impl(dynamic_tree)

        # Очередь задач для главного потока
        self._task_queue = queue.Queue()
        # Запускаем опрос очереди в главном потоке
        self._poll_queue()

    # ══════════════════════════════════════════════════════════
    #  Диспетчер потоков — очередь задач
    # ══════════════════════════════════════════════════════════

    def _poll_queue(self):
        """Опрашивает очередь задач. Вызывается только в главном потоке."""
        try:
            while True:
                task = self._task_queue.get_nowait()
                func, args, kwargs, result_box, done_event = task
                try:
                    result = func(*args, **kwargs)
                    if result_box is not None:
                        result_box["result"] = result
                except Exception as exc:
                    if result_box is not None:
                        result_box["error"] = exc
                finally:
                    if done_event is not None:
                        done_event.set()
        except queue.Empty:
            pass
        # Планируем следующий опрос (100 мс)
        self.static_tree.after(100, self._poll_queue)

    def _fire_and_forget(self, func, *args, **kwargs):
        """Ставит задачу в очередь. Результат не возвращается."""
        if threading.current_thread() is threading.main_thread():
            func(*args, **kwargs)
        else:
            self._task_queue.put((func, args, kwargs, None, None))

    def _call_and_wait(self, func, *args, **kwargs):
        """Ставит задачу в очередь, ждёт результат (таймаут 5 сек)."""
        if threading.current_thread() is threading.main_thread():
            return func(*args, **kwargs)

        result_box = {"result": None, "error": None}
        done = threading.Event()
        self._task_queue.put((func, args, kwargs, result_box, done))

        if not done.wait(timeout=5.0):
            raise TimeoutError("Главный поток не ответил за 5 секунд")
        if result_box["error"] is not None:
            raise result_box["error"]
        return result_box["result"]

    # ──────────────────────────────────────────────────────────
    #  Создание / обновление индексов
    # ──────────────────────────────────────────────────────────

    @staticmethod
    def WASTE_buttonHandler():
        print("runned WASTE")

    def _build_index_impl(self, tree):
        index = {}
        for item in tree.get_children():
            values = tree.item(item, "values")
            if values:
                index[values[0]] = item
        return index

    def refresh_indexes(self):
        self._fire_and_forget(self._refresh_indexes_impl)

    def _refresh_indexes_impl(self):
        self._static_index = self._build_index_impl(self.static_tree)
        self._dynamic_index = self._build_index_impl(self.dynamic_tree)

    # ──────────────────────────────────────────────────────────
    #  Статика — значения
    # ──────────────────────────────────────────────────────────

    def static_set(self, param, col, value):
        self._fire_and_forget(self._static_set_impl, param, col, value)

    def _static_set_impl(self, param, col, value):
        item = self._static_index.get(param)
        if item is None:
            raise KeyError(f"Параметр '{param}' не найден в таблице «Статика»")
        if col not in self.STATIC_VALUE_COLS:
            raise ValueError(f"Недопустимая колонка '{col}'. Допустимы: {self.STATIC_VALUE_COLS}")
        self.static_tree.set(item, col, str(value))

    def static_get(self, param, col):
        return self._call_and_wait(self._static_get_impl, param, col)

    def _static_get_impl(self, param, col):
        item = self._static_index.get(param)
        if item is None:
            raise KeyError(f"Параметр '{param}' не найден в таблице «Статика»")
        if col not in self.STATIC_VALUE_COLS:
            raise ValueError(f"Недопустимая колонка '{col}'. Допустимы: {self.STATIC_VALUE_COLS}")
        return self.static_tree.set(item, col)

    def static_set_row(self, param, bids="", asks=""):
        self._fire_and_forget(self._static_set_row_impl, param, bids, asks)

    def _static_set_row_impl(self, param, bids="", asks=""):
        self._static_set_impl(param, "bids", bids)
        self._static_set_impl(param, "asks", asks)

    def static_get_row(self, param):
        return self._call_and_wait(self._static_get_row_impl, param)

    def _static_get_row_impl(self, param):
        return {
            "bids": self._static_get_impl(param, "bids"),
            "asks": self._static_get_impl(param, "asks"),
        }

    def static_clear(self):
        self._fire_and_forget(self._static_clear_impl)

    def _static_clear_impl(self):
        for item in self.static_tree.get_children():
            for col in self.STATIC_VALUE_COLS:
                self.static_tree.set(item, col, "")

    def static_clear_row(self, param):
        self._fire_and_forget(self._static_set_row_impl, param, "", "")

    # ──────────────────────────────────────────────────────────
    #  Статика — цвет текста
    # ──────────────────────────────────────────────────────────

    def static_set_color(self, param, color):
        self._fire_and_forget(self._static_set_color_impl, param, color)

    def _static_set_color_impl(self, param, color):
        item = self._static_index.get(param)
        if item is None:
            raise KeyError(f"Параметр '{param}' не найден в таблице «Статика»")
        self._apply_foreground(self.static_tree, item, color)

    def static_reset_color(self, param):
        self._fire_and_forget(self._static_set_color_impl, param, None)

    # ──────────────────────────────────────────────────────────
    #  Динамика — значения
    # ──────────────────────────────────────────────────────────

    def dynamic_set(self, param, cycle, side, value):
        self._fire_and_forget(self._dynamic_set_impl, param, cycle, side, value)

    def _dynamic_set_impl(self, param, cycle, side, value):
        item = self._dynamic_index.get(param)
        if item is None:
            raise KeyError(f"Параметр '{param}' не найден в таблице «Динамика»")
        col = self._dynamic_col_name(cycle, side)
        self.dynamic_tree.set(item, col, str(value))

    def dynamic_get(self, param, cycle, side):
        return self._call_and_wait(self._dynamic_get_impl, param, cycle, side)

    def _dynamic_get_impl(self, param, cycle, side):
        item = self._dynamic_index.get(param)
        if item is None:
            raise KeyError(f"Параметр '{param}' не найден в таблице «Динамика»")
        col = self._dynamic_col_name(cycle, side)
        return self.dynamic_tree.set(item, col)

    def dynamic_set_row(self, param,
                         cycle1_bids="", cycle1_asks="",
                         cycle5_bids="", cycle5_asks="",
                         cycle10_bids="", cycle10_asks=""):
        self._fire_and_forget(
            self._dynamic_set_row_impl,
            param, cycle1_bids, cycle1_asks,
            cycle5_bids, cycle5_asks,
            cycle10_bids, cycle10_asks,
        )

    def _dynamic_set_row_impl(self, param,
                               cycle1_bids="", cycle1_asks="",
                               cycle5_bids="", cycle5_asks="",
                               cycle10_bids="", cycle10_asks=""):
        mapping = {
            ("1 цикл", "bids"): cycle1_bids,
            ("1 цикл", "asks"): cycle1_asks,
            ("5 цикл.", "bids"): cycle5_bids,
            ("5 цикл.", "asks"): cycle5_asks,
            ("10 цикл.", "bids"): cycle10_bids,
            ("10 цикл.", "asks"): cycle10_asks,
        }
        for (cycle, side), val in mapping.items():
            self._dynamic_set_impl(param, cycle, side, val)

    def dynamic_get_row(self, param):
        return self._call_and_wait(self._dynamic_get_row_impl, param)

    def _dynamic_get_row_impl(self, param):
        result = {}
        for cycle in self.DYNAMIC_CYCLES:
            for side in self.DYNAMIC_SIDES:
                result[(cycle, side)] = self._dynamic_get_impl(param, cycle, side)
        return result

    def dynamic_clear(self):
        self._fire_and_forget(self._dynamic_clear_impl)

    def _dynamic_clear_impl(self):
        for item in self.dynamic_tree.get_children():
            for cycle in self.DYNAMIC_CYCLES:
                for side in self.DYNAMIC_SIDES:
                    col = self._dynamic_col_name(cycle, side)
                    self.dynamic_tree.set(item, col, "")

    def dynamic_clear_row(self, param):
        self._fire_and_forget(self._dynamic_set_row_impl, param)

    # ──────────────────────────────────────────────────────────
    #  Динамика — цвет текста
    # ──────────────────────────────────────────────────────────

    def dynamic_set_color(self, param, color):
        self._fire_and_forget(self._dynamic_set_color_impl, param, color)

    def _dynamic_set_color_impl(self, param, color):
        item = self._dynamic_index.get(param)
        if item is None:
            raise KeyError(f"Параметр '{param}' не найден в таблице «Динамика»")
        self._apply_foreground(self.dynamic_tree, item, color)

    def dynamic_reset_color(self, param):
        self._fire_and_forget(self._dynamic_set_color_impl, param, None)

    # ──────────────────────────────────────────────────────────
    #  Внутренние утилиты
    # ──────────────────────────────────────────────────────────

    def _apply_foreground(self, tree, item, color):
        current_tags = tree.item(item, "tags")
        other_tags = [t for t in current_tags
                      if not t.startswith(self._COLOR_TAG_PREFIX)]
        if color:
            tag_name = f"{self._COLOR_TAG_PREFIX}{color}"
            tree.tag_configure(tag_name, foreground=color)
            new_tags = tuple(other_tags) + (tag_name,)
        else:
            new_tags = tuple(other_tags)
        tree.item(item, tags=new_tags)

    @staticmethod
    def _dynamic_col_name(cycle, side):
        if cycle not in VisualTablesInterface.DYNAMIC_CYCLES:
            raise ValueError(f"Недопустимый цикл '{cycle}'. Допустимы: {VisualTablesInterface.DYNAMIC_CYCLES}")
        if side not in VisualTablesInterface.DYNAMIC_SIDES:
            raise ValueError(f"Недопустимая сторона '{side}'. Допустимы: {VisualTablesInterface.DYNAMIC_SIDES}")
        return f"{cycle}\n{side}"

    # ──────────────────────────────────────────────────────────
    #  Справочные методы
    # ──────────────────────────────────────────────────────────

    def static_params(self):
        return self._call_and_wait(lambda: list(self._static_index.keys()))

    def dynamic_params(self):
        return self._call_and_wait(lambda: list(self._dynamic_index.keys()))

    def static_item_id(self, param):
        return self._call_and_wait(lambda: self._static_index.get(param))

    def dynamic_item_id(self, param):
        return self._call_and_wait(lambda: self._dynamic_index.get(param))
