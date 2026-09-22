"""
tables_interface.py — интерфейс для удобного доступа к ячейкам таблиц «Статика» и «Динамика».

Использование:
    from visual.tables_interface import TablesInterface

    interface = TablesInterface(window.static_tree, window.dynamic_tree)

    # Статика
    interface.static_set("Спрэд", "bids", "0.0234")
    value = interface.static_get("Спрэд", "bids")

    # Динамика
    interface.dynamic_set("Количество стен (bids/asks)", "1 цикл", "bids", "42")
    interface.dynamic_set_row(
        "Количество стен (bids/asks)",
        cycle1_bids="42", cycle1_asks="38",
        cycle5_bids="45", cycle5_asks="41",
        cycle10_bids="50", cycle10_asks="47",
    )

    # Цвет текста строки
    interface.static_set_color("Спрэд", "#FF0000")   # красный
    interface.static_reset_color("Спрэд")            # сброс

    interface.dynamic_set_color("Количество стен (bids/asks)", "#00AA00")
    interface.dynamic_reset_color("Количество стен (bids/asks)")

    SUPER:
        interface = TablesInterface(Window.static_tree, Window.dynamic_tree)

        # Пример записи
        interface.static_set("Спрэд", "bids", "0.0123")
        interface.dynamic_set("Количество стен (bids/asks)", "5 цикл.", "asks", "27")

        
        # Покрасить текст строки «Спрэд» в красный
        interface.static_set_color("Спрэд", "#FF0000")

        # Сбросить обратно
        interface.static_reset_color("Спрэд")

        # В динамике — зелёный текст для строки «Количество стен»
        interface.dynamic_set_color("Количество стен (bids/asks)", "#00AA00")
        interface.dynamic_reset_color("Количество стен (bids/asks)")
"""
from network.DataBase.DataBaseManager import DataBaseManager


class TablesInterface():
    """Интерфейс для работы с таблицами Treeview («Статика» и «Динамика»)."""

    STATIC_VALUE_COLS = ("bids", "asks")
    DYNAMIC_CYCLES = ("1 цикл", "5 цикл.", "10 цикл.")
    DYNAMIC_SIDES = ("bids", "asks")

    # Префикс для цветовых тегов, чтобы не конфликтовать с even/odd/section
    _COLOR_TAG_PREFIX = "_fg_"



    def __init__(self, static_tree, dynamic_tree):
        # self.db.connect()
        print("runned table interfaces, db")
        self._static = static_tree
        self._dynamic = dynamic_tree
        self._static_index = self._build_index(static_tree)
        self._dynamic_index = self._build_index(dynamic_tree)

    @staticmethod
    def WASTE_buttonHandler():
        print("runned WASTE")
        # TablesInterface.db.fill_database_in_background([BybitExchange.Orderbook.asksPrice, BybitExchange.Orderbook.asksSize],[BybitExchange.Orderbook.bidsPrice, BybitExchange.Orderbook.bidsSize])

    @staticmethod
    def _build_index(tree):
        """Строит словарь: {значение первой колонки: item_id}."""
        index = {}
        for item in tree.get_children():
            values = tree.item(item, "values")
            if values:
                key = values[0]
                index[key] = item
        return index

    def refresh_indexes(self):
        """Перестроить индексы, если строки изменялись."""
        self._static_index = self._build_index(self._static)
        self._dynamic_index = self._build_index(self._dynamic)

    # ============================================================
    #  Статика — значения
    # ============================================================

    def static_set(self, param, col, value):
        item = self._static_index.get(param)
        if item is None:
            raise KeyError(f"Параметр '{param}' не найден в таблице «Статика»")
        if col not in self.STATIC_VALUE_COLS:
            raise ValueError(f"Недопустимая колонка '{col}'. Допустимы: {self.STATIC_VALUE_COLS}")
        self._static.set(item, col, str(value))

    def static_get(self, param, col):
        item = self._static_index.get(param)
        if item is None:
            raise KeyError(f"Параметр '{param}' не найден в таблице «Статика»")
        if col not in self.STATIC_VALUE_COLS:
            raise ValueError(f"Недопустимая колонка '{col}'. Допустимы: {self.STATIC_VALUE_COLS}")
        return self._static.set(item, col)

    def static_set_row(self, param, bids="", asks=""):
        self.static_set(param, "bids", bids)
        self.static_set(param, "asks", asks)

    def static_get_row(self, param):
        return {
            "bids": self.static_get(param, "bids"),
            "asks": self.static_get(param, "asks"),
        }

    def static_clear(self):
        for item in self._static.get_children():
            for col in self.STATIC_VALUE_COLS:
                self._static.set(item, col, "")

    def static_clear_row(self, param):
        self.static_set_row(param, "", "")

    # ============================================================
    #  Статика — цвет текста
    # ============================================================

    def static_set_color(self, param, color):
        """Установить цвет текста для строки.

        :param param: название параметра
        :param color: HEX-строка, например "#FF0000" (красный), "#00AA00" (зелёный)
        """
        item = self._static_index.get(param)
        if item is None:
            raise KeyError(f"Параметр '{param}' не найден в таблице «Статика»")
        self._apply_foreground(self._static, item, color)

    def static_reset_color(self, param):
        """Сбросить цвет текста строки к значению по умолчанию."""
        item = self._static_index.get(param)
        if item is None:
            raise KeyError(f"Параметр '{param}' не найден в таблице «Статика»")
        self._apply_foreground(self._static, item, None)

    # ============================================================
    #  Динамика — значения
    # ============================================================

    def dynamic_set(self, param, cycle, side, value):
        item = self._dynamic_index.get(param)
        if item is None:
            raise KeyError(f"Параметр '{param}' не найден в таблице «Динамика»")
        col = self._dynamic_col_name(cycle, side)
        self._dynamic.set(item, col, str(value))

    def dynamic_get(self, param, cycle, side):
        item = self._dynamic_index.get(param)
        if item is None:
            raise KeyError(f"Параметр '{param}' не найден в таблице «Динамика»")
        col = self._dynamic_col_name(cycle, side)
        return self._dynamic.set(item, col)

    def dynamic_set_row(self, param,
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
            self.dynamic_set(param, cycle, side, val)

    def dynamic_get_row(self, param):
        result = {}
        for cycle in self.DYNAMIC_CYCLES:
            for side in self.DYNAMIC_SIDES:
                result[(cycle, side)] = self.dynamic_get(param, cycle, side)
        return result

    def dynamic_clear(self):
        for item in self._dynamic.get_children():
            for cycle in self.DYNAMIC_CYCLES:
                for side in self.DYNAMIC_SIDES:
                    col = self._dynamic_col_name(cycle, side)
                    self._dynamic.set(item, col, "")

    def dynamic_clear_row(self, param):
        self.dynamic_set_row(param)

    # ============================================================
    #  Динамика — цвет текста
    # ============================================================

    def dynamic_set_color(self, param, color):
        """Установить цвет текста для строки.

        :param param: название параметра
        :param color: HEX-строка, например "#FF0000"
        """
        item = self._dynamic_index.get(param)
        if item is None:
            raise KeyError(f"Параметр '{param}' не найден в таблице «Динамика»")
        self._apply_foreground(self._dynamic, item, color)

    def dynamic_reset_color(self, param):
        """Сбросить цвет текста строки к значению по умолчанию."""
        item = self._dynamic_index.get(param)
        if item is None:
            raise KeyError(f"Параметр '{param}' не найден в таблице «Динамика»")
        self._apply_foreground(self._dynamic, item, None)

    # ============================================================
    #  Внутренние утилиты
    # ============================================================

    def _apply_foreground(self, tree, item, color):
        """Применяет или сбрасывает цвет текста для строки.

        Treeview не поддерживает цвет отдельных ячеек — только целых строк.
        Метод создаёт динамический тег с нужным foreground и добавляет его
        к существующим тегам строки (even/odd/section), не затирая их.

        :param tree: виджет Treeview
        :param item: item_id строки
        :param color: HEX-цвет или None для сброса
        """
        current_tags = tree.item(item, "tags")

        # Разделяем: цветовые теги отдельно, остальные — отдельно
        other_tags = [t for t in current_tags
                      if not t.startswith(self._COLOR_TAG_PREFIX)]
        color_tags = [t for t in current_tags
                      if t.startswith(self._COLOR_TAG_PREFIX)]

        if color:
            tag_name = f"{self._COLOR_TAG_PREFIX}{color}"
            # Конфигурируем тег с нужным foreground
            tree.tag_configure(tag_name, foreground=color)
            # Цветовой тег ставим последним — он перекрывает foreground
            # от тегов section и других
            new_tags = tuple(other_tags) + (tag_name,)
        else:
            # Сброс: убираем цветовой тег, оставляем только остальные
            new_tags = tuple(other_tags)

        tree.item(item, tags=new_tags)

    @staticmethod
    def _dynamic_col_name(cycle, side):
        if cycle not in TablesInterface.DYNAMIC_CYCLES:
            raise ValueError(f"Недопустимый цикл '{cycle}'. Допустимы: {TablesInterface.DYNAMIC_CYCLES}")
        if side not in TablesInterface.DYNAMIC_SIDES:
            raise ValueError(f"Недопустимая сторона '{side}'. Допустимы: {TablesInterface.DYNAMIC_SIDES}")
        return f"{cycle}\n{side}"

    def static_params(self):
        return list(self._static_index.keys())

    def dynamic_params(self):
        return list(self._dynamic_index.keys())

    def static_item_id(self, param):
        return self._static_index.get(param)

    def dynamic_item_id(self, param):
        return self._dynamic_index.get(param)
