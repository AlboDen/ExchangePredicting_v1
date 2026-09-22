import tkinter as tk
from tkinter import ttk
import os
import gc
import random
from datetime import datetime, timedelta
# from Calculations.statisticsMethods import Statistic
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk,
)
from matplotlib.figure import Figure

from network.BybitExchange import BybitExchange
from visual.buttonHandlers import ButtonHandlers
# from visual.buttonHandlers import ButtonHandlers
from visual.graph import Graph
from visual.visualTablesDataInterface import VisualTablesInterface

# from visual.visualTablesDataInterface import VisualTablesInterface

SPLIT_PARAMS = {
    "Площадь под линией регрессии (bids/asks)",
    "Количество точек после фильтрации (bids/asks)",
    "Количество точек после фильтрации под\nлинией регрессии (bids/asks)",
    "Количество точек в ближайшей трети (1/3)\nплощади к равновесной цене (bids/asks)",
    "Количество точек в средней трети (2/3)\nплощади к равновесной цене (bids/asks)",
    "Количество точек в дальней трети площади\n(3/3) к равновесной цене (bids/asks)",
    "Количество стен (bids/asks)",
}


class Window(tk.Tk):
    info_label = None
    static_tree = None
    dynamic_tree = None

    COLORS = {
        "bg_main": "#F5F6F7",
        "bg_panel": "#ECEFF1",
        "bg_notebook": "#FFFFFF",
        "text_main": "#000000",
        "text_muted": "#7F8C8D",
        "accent": "#2E86AB",
        "accent_light": "#A2DBEA",
        "btn_bg": "#E74C3C",
        "btn_hover": "#C0392B",
        "btn_small_bg": "#DDE8ED",
        "btn_small_hover": "#C8D5DC",
        "btn_freeze_bg": "#3498DB",
        "btn_freeze_hover": "#2980B9",
        "btn_freeze_active_bg": "#E67E22",
        "btn_freeze_active_hover": "#D35400",
        "treeview_row": "#FFFFFF",
        "treeview_alt": "#EEF2F5",
        "treeview_border": "#000000",   # Чёрные границы
        "border": "#000000",
        "section_bg": "#E8EEF2",
    }

    TablesInterface = None

    def __init__(self):
        super().__init__()



        self.title("Прогноз ликвидности биржевого актива для наращивания капитала ООО 'Эквивалент'")
        self.minsize(700, 400)
        # self.state('zoomed')

        self.configure(bg=self.COLORS["bg_main"])
        self._setup_styles()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Флаг заморозки для графиков
        self.frozen = False

        # Словарь для хранения canvas-ов и тулбаров по вкладкам
        self.graph_canvases = {}

        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель — график
        graph_frame = ttk.Frame(paned_window, padding=10)
        paned_window.add(graph_frame, weight=4)

        # --- Верхняя строка: инфо-лейбл + 5 кнопок ---
        top_bar = ttk.Frame(graph_frame)
        top_bar.pack(fill=tk.X, pady=(0, 10))

        self.info_label = tk.Label(
            top_bar,
            text="Ожидание данных...",
            anchor="w",
            fg=self.COLORS["text_main"],
            bg=self.COLORS["bg_notebook"],
            font=("Segoe UI", 10, "bold")
        )
        self.info_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        Window.info_label = self.info_label

        interval_buttons_frame = ttk.Frame(top_bar)
        interval_buttons_frame.pack(side=tk.RIGHT)

        for label in ["10 секунд", "30 секунд", "60 секунд", "5 минут", "30 минут"]:
            ttk.Button(
                interval_buttons_frame,
                text=label,
                style="Small.TButton",
                command=lambda l=label: self._on_interval_click(l)
            ).pack(side=tk.LEFT, padx=2)

        # --- Notebook с графиками ---
        self.notebook = ttk.Notebook(graph_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка «Распределение стакана»
        graph_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(graph_tab, text="Распределение стакана")

        self.equilibrium_label = tk.Label(
            graph_tab,
            text="Равновесная цена равна {} USD",
            font=("Segoe UI", 12, "bold"),
            fg=self.COLORS["text_main"],
            bg=self.COLORS["bg_notebook"],
            anchor="center"
        )
        self.equilibrium_label.pack(fill=tk.X, pady=(5, 5))

        orderbook_container = ttk.Frame(graph_tab)
        orderbook_container.pack(fill=tk.BOTH, expand=True)

        canvases_before = set(id(w) for w in self._all_widgets(self))
        Graph.Orderbook.initOrderbook(orderbook_container)
        new_canvases = [w for w in self._all_widgets(self)
                        if id(w) not in canvases_before and isinstance(w, tk.Canvas)]
        self._apply_axis_labels_to_canvases(new_canvases)
        self._add_toolbar_and_freeze(graph_tab, "orderbook", new_canvases)

        # Вкладка «Свечи»
        candle_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(candle_tab, text="Свечи")
        candle_canvas = self._init_candlestick(candle_tab)
        self._add_toolbar_and_freeze(candle_tab, "candle", [candle_canvas])

        # Вкладка «...»
        _tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(_tab, text="...")

        # Правая панель — управление
        control_frame = ttk.Frame(paned_window, padding=15)
        paned_window.add(control_frame, weight=1)

        control_notebook = ttk.Notebook(control_frame)
        control_notebook.pack(fill=tk.BOTH, expand=True)

        self._build_static_tab(control_notebook)
        self._build_dynamic_tab(control_notebook)

        other_tab = ttk.Frame(control_notebook, padding=10)
        control_notebook.add(other_tab, text="Ещё")
        tk.Label(
            other_tab,
            text="Дополнительные инструменты",
            font=("Segoe UI", 10),
            fg=self.COLORS["text_muted"],
            bg=self.COLORS["bg_notebook"]
        ).pack(anchor="w")

        ttk.Button(
            other_tab,
            text="пыньк",
            style="Contrast.TButton",
            # command=self.waste_fff
            # command=VisualTablesInterface.WASTE_buttonHandler
        ).place(x=20, y=150, width=140, height=45)

        # print("PPPPPPPPPPPPPPPPPPPPPP",self.static_tree)
        VisualTablesInterface.itSelf = VisualTablesInterface(self.static_tree, self.dynamic_tree)
        VisualTablesInterface.static_tree = self.static_tree
        VisualTablesInterface.dynamic_tree = self.dynamic_tree

    def waste_fff(self):
        pass
        # interface = TablesInterface(Window.static_tree, Window.dynamic_tree)
        #
        # # Пример записи
        # interface.static_set("Спрэд", "bids", "0.0123")
        # interface.dynamic_set("Количество стен (bids/asks)", "5 цикл.", "asks", "27")
        # interface.static_set_color("Спрэд", "#FF0000")

    # ============================================================
    #  Тулбар + заморозка для вкладок с графиками
    # ============================================================



    def _add_toolbar_and_freeze(self, tab, key, canvas_widgets):
        """Добавляет панель с кнопкой «Заморозить» и matplotlib-тулбаром."""
        if not canvas_widgets:
            return

        # Находим FigureCanvasTkAgg по tk.Canvas
        fig_canvas = None
        try:
            for obj in gc.get_objects():
                if hasattr(obj, 'figure') and hasattr(obj, '_tkcanvas'):
                    if obj._tkcanvas in canvas_widgets:
                        fig_canvas = obj
                        break
        except Exception:
            pass

        if fig_canvas is None:
            return

        self.graph_canvases[key] = fig_canvas

        # Панель управления под графиком
        toolbar_frame = ttk.Frame(tab)
        toolbar_frame.pack(fill=tk.X, pady=(5, 0))

        # Кнопка «Заморозить»
        freeze_btn = ttk.Button(
            toolbar_frame,
            text="Заморозить",
            style="Freeze.TButton",
            command=lambda: self._toggle_freeze(key, freeze_btn)
        )
        freeze_btn.pack(side=tk.LEFT, padx=(0, 10))

        # matplotlib-тулбар (зум, панорама, сохранение, домой)
        try:
            toolbar = NavigationToolbar2Tk(fig_canvas, toolbar_frame)
            toolbar.update()
            # Тулбар сам упаковывается, но убеждаемся, что он справа
            toolbar.pack(side=tk.LEFT)
        except Exception:
            pass

    def _toggle_freeze(self, key, btn):
        """Переключает заморозку для конкретного графика."""
        if key not in self.graph_canvases:
            return

        fig_canvas = self.graph_canvases[key]
        fig = fig_canvas.figure

        if not hasattr(fig, '_frozen'):
            fig._frozen = False

        fig._frozen = not fig._frozen

        if fig._frozen:
            btn.config(text="Разморозить", style="FreezeActive.TButton")
            # Останавливаем анимации, если есть
            for ax in fig.get_axes():
                for anim in getattr(ax, '_anim', []):
                    try:
                        anim.event_source.stop()
                    except Exception:
                        pass
        else:
            btn.config(text="Заморозить", style="Freeze.TButton")
            for ax in fig.get_axes():
                for anim in getattr(ax, '_anim', []):
                    try:
                        anim.event_source.start()
                    except Exception:
                        pass
            fig.canvas.draw()

    def is_graph_frozen(self, key="orderbook"):
        """Внешний код может проверить, заморожен ли график."""
        if key not in self.graph_canvases:
            return False
        fig = self.graph_canvases[key].figure
        return getattr(fig, '_frozen', False)

    # ============================================================
    #  Поиск виджетов и подписи осей
    # ============================================================

    @staticmethod
    def _all_widgets(root):
        result = []
        stack = [root]
        while stack:
            w = stack.pop()
            result.append(w)
            try:
                stack.extend(w.winfo_children())
            except tk.TclError:
                pass
        return result

    def _apply_axis_labels_to_canvases(self, canvas_widgets):
        if not canvas_widgets:
            return
        try:
            for obj in gc.get_objects():
                if hasattr(obj, 'figure') and hasattr(obj, '_tkcanvas'):
                    if obj._tkcanvas in canvas_widgets:
                        fig = obj.figure
                        for ax in fig.get_axes():
                            ax.set_xlabel(
                                "Цена актива, USD",
                                fontsize=12,
                                color=self.COLORS["text_main"]
                            )
                            ax.set_ylabel(
                                "Количество спроса актива, ед.",
                                fontsize=12,
                                color=self.COLORS["text_main"],
                                rotation=90,
                                labelpad=10
                            )
                        fig.canvas.draw()
                        return
        except Exception:
            pass

    # ============================================================
    #  Вкладка «Статика»
    # ============================================================

    def _build_static_tab(self, parent):
        static_tab = ttk.Frame(parent, padding=10)
        parent.add(static_tab, text="Статика")

        tk.Label(
            static_tab,
            text="Параметры расчёта",
            font=("Segoe UI", 11, "bold"),
            fg=self.COLORS["accent"],
            bg=self.COLORS["bg_notebook"]
        ).pack(anchor="w", pady=(0, 15))

        self.static_tree = ttk.Treeview(
            static_tab,
            columns=("Параметр", "bids", "asks"),
            show="headings",
            selectmode="none"
        )
        Window.static_tree = self.static_tree

        self.static_tree.heading("Параметр", text="Параметр")
        self.static_tree.heading("bids", text="bids")
        self.static_tree.heading("asks", text="asks")

        self.static_tree.column("Параметр", width=200, anchor="center", stretch=True)
        self.static_tree.column("bids", width=80, anchor="center", stretch=False)
        self.static_tree.column("asks", width=80, anchor="center", stretch=False)

        static_scroll = ttk.Scrollbar(static_tab, orient="vertical",
                                       command=self.static_tree.yview)
        self.static_tree.configure(yscrollcommand=static_scroll.set)
        self.static_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        static_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        static_params = [
            "Спрэд",
            "Способ регрессии (bids)",
            "Способ регрессии (Asks)",
            "Площадь под линией регрессии (bids/asks)",
            "Отношение площадей под линиями регрессии",
            "Количество точек после фильтрации (bids/asks)",
            "Количество точек после фильтрации под\nлинией регрессии (bids/asks)",
            "Количество точек в ближайшей трети (1/3)\nплощади к равновесной цене (bids/asks)",
            "Количество точек в средней трети (2/3)\nплощади к равновесной цене (bids/asks)",
            "Количество точек в дальней трети площади\n(3/3) к равновесной цене (bids/asks)",
            "ДОПОЛНИТЕЛЬНО",
            "Отношение коэффициентов линейной регрессии",
            "Отношение площадей прямоугольных полигонов",
            "Количество стен (bids/asks)",
            "Отношение взвешенных стен",
        ]
        for param in static_params:
            if param == "ДОПОЛНИТЕЛЬНО":
                self.static_tree.insert("", tk.END, values=(param, "", ""),
                                        tags=("section",))
            else:
                self.static_tree.insert("", tk.END, values=(param, "", ""))

        self.static_tree.tag_configure("even", background=self.COLORS["treeview_alt"])
        self.static_tree.tag_configure("odd", background=self.COLORS["treeview_row"])
        self.static_tree.tag_configure("section",
                                       background=self.COLORS["section_bg"],
                                       font=("Segoe UI", 10, "bold"))

        for i, item in enumerate(self.static_tree.get_children()):
            tags = self.static_tree.item(item, "tags")
            if "section" in tags:
                continue
            if i % 2 == 0:
                self.static_tree.item(item, tags=("even",))
            else:
                self.static_tree.item(item, tags=("odd",))

    # ============================================================
    #  Вкладка «Динамика»
    # ============================================================

    def _build_dynamic_tab(self, parent):
        dynamic_tab = ttk.Frame(parent, padding=10)
        parent.add(dynamic_tab, text="Динамика")

        tk.Label(
            dynamic_tab,
            text="Метрики динамики по циклам",
            font=("Segoe UI", 11, "bold"),
            fg=self.COLORS["accent"],
            bg=self.COLORS["bg_notebook"]
        ).pack(anchor="w", pady=(0, 15))

        col_names = ("Параметр",
                     "1 цикл\nbids", "1 цикл\nasks",
                     "5 цикл.\nbids", "5 цикл.\nasks",
                     "10 цикл.\nbids", "10 цикл.\nasks")
        self.dynamic_tree = ttk.Treeview(
            dynamic_tab,
            columns=col_names,
            show="headings",
            selectmode="none"
        )
        Window.dynamic_tree = self.dynamic_tree
        for name in col_names:
            self.dynamic_tree.heading(name, text=name)

        self.dynamic_tree.column("Параметр", width=150, anchor="center", stretch=True)
        for name in col_names[1:]:
            self.dynamic_tree.column(name, width=55, anchor="center", stretch=False)

        dynamic_scroll = ttk.Scrollbar(dynamic_tab, orient="vertical",
                                        command=self.dynamic_tree.yview)
        self.dynamic_tree.configure(yscrollcommand=dynamic_scroll.set)
        self.dynamic_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dynamic_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        dynamic_params = [
            "Спрэд",
            "Способ регрессии (bids)",
            "Способ регрессии (Asks)",
            "Площадь под линией регрессии (bids/asks)",
            "Отношение площадей под линиями регрессии",
            "Количество точек после фильтрации (bids/asks)",
            "Количество точек после фильтрации под\nлинией регрессии (bids/asks)",
            "Количество точек в ближайшей трети (1/3)\nплощади к равновесной цене (bids/asks)",
            "Количество точек в средней трети (2/3)\nплощади к равновесной цене (bids/asks)",
            "Количество точек в дальней трети площади\n(3/3) к равновесной цене (bids/asks)",
            "ДОПОЛНИТЕЛЬНО",
            "Отношение коэффициентов линейной регрессии",
            "Отношение площадей прямоугольных полигонов",
            "Количество стен (bids/asks)",
            "Отношение взвешенных стен",
            "ИЗ ДИНАМИКИ по диаграмме спроса",
            "Отклонение по модулю",
            "Отклонение по цене",
            "Отклонение по значению",
            "ИЗ ДИНАМИКИ свечного графика",
            "Отклонение по цене",
            "Отклонение максимальной цены",
            "Отклонение минимальной цены",
            "Отклонение цены закрытия",
            "...",
        ]
        for param in dynamic_params:
            if param == "ДОПОЛНИТЕЛЬНО":
                self.dynamic_tree.insert("", tk.END,
                                         values=(param, "", "", "", "", "", ""),
                                         tags=("section",))
            else:
                self.dynamic_tree.insert("", tk.END,
                                         values=(param, "", "", "", "", "", ""))

        self.dynamic_tree.tag_configure("even", background=self.COLORS["treeview_alt"])
        self.dynamic_tree.tag_configure("odd", background=self.COLORS["treeview_row"])
        self.dynamic_tree.tag_configure("section",
                                        background=self.COLORS["section_bg"],
                                        font=("Segoe UI", 10, "bold"))

        for i, item in enumerate(self.dynamic_tree.get_children()):
            tags = self.dynamic_tree.item(item, "tags")
            if "section" in tags:
                continue
            if i % 2 == 0:
                self.dynamic_tree.item(item, tags=("even",))
            else:
                self.dynamic_tree.item(item, tags=("odd",))

    # ============================================================
    #  Свечной график
    # ============================================================

    def _init_candlestick(self, parent):
        fig = Figure(figsize=(8, 5), facecolor=self.COLORS["bg_notebook"])
        ax = fig.add_subplot(111)
        ax.set_facecolor("#FAFBFC")

        n_candles = 30
        base_price = 65000
        dates = [datetime(2026, 9, 1) + timedelta(days=i) for i in range(n_candles)]
        opens = [base_price + random.uniform(-200, 200)]
        for i in range(1, n_candles):
            opens.append(opens[-1] + random.uniform(-300, 300))
        highs = [o + random.uniform(50, 400) for o in opens]
        lows = [o - random.uniform(50, 400) for o in opens]
        closes = [o + random.uniform(-200, 200) for o in opens]

        for i in range(n_candles):
            color = "#2ECC71" if closes[i] >= opens[i] else "#E74C3C"
            body_bottom = min(opens[i], closes[i])
            body_height = abs(closes[i] - opens[i])
            ax.bar(i, body_height, bottom=body_bottom, width=0.6,
                   color=color, edgecolor=color, linewidth=1)
            ax.plot([i, i], [lows[i], highs[i]], color=color, linewidth=1.2)

        ax.set_xticks(range(0, n_candles, 5))
        ax.set_xticklabels([dates[i].strftime("%d.%m") for i in range(0, n_candles, 5)],
                          fontsize=9, rotation=30)
        ax.set_xlabel("Дата", fontsize=11, color=self.COLORS["text_main"])
        ax.set_ylabel("Цена актива, USD", fontsize=11, color=self.COLORS["text_main"])
        ax.set_title("Свечной график (тестовые данные)", fontsize=13,
                     color=self.COLORS["text_main"], pad=15)
        ax.grid(True, alpha=0.3, linestyle="--")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        return canvas._tkcanvas

    # ============================================================
    #  Прочее
    # ============================================================

    def _on_interval_click(self, label):
        self.info_label.config(text=f"Интервал: {label}")

    def update_equilibrium_price(self, price):
        self.equilibrium_label.config(text=f"Равновесная цена равна {price} USD")

    def _on_close(self):
        try:
            self.destroy()
        except Exception:
            pass
        os._exit(0)

    # ============================================================
    #  Стили
    # ============================================================

    def _setup_styles(self):
        style = ttk.Style()

        style.configure(".", background=self.COLORS["bg_main"],
                        foreground=self.COLORS["text_main"])
        style.configure("TFrame", background=self.COLORS["bg_main"])
        style.configure("TLabelframe", background=self.COLORS["bg_main"])

        style.configure("TNotebook", background=self.COLORS["bg_panel"], borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=self.COLORS["bg_panel"],
                        foreground=self.COLORS["text_muted"],
                        padding=[12, 8],
                        font=("Segoe UI", 9))
        style.map("TNotebook.Tab",
                  background=[("selected", self.COLORS["bg_notebook"])],
                  foreground=[("selected", self.COLORS["accent"])])

        # Treeview — чёрные границы
        style.configure("Treeview",
                        rowheight=48,
                        fieldbackground=self.COLORS["treeview_row"],
                        bordercolor=self.COLORS["treeview_border"],
                        borderwidth=2,
                        relief="solid",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#CFD8DC",
                        foreground=self.COLORS["text_main"],
                        relief="solid",
                        borderwidth=1,
                        bordercolor=self.COLORS["treeview_border"],
                        font=("Segoe UI", 9, "bold"))
        style.map("Treeview.Heading", relief=[("pressed", "solid")])

        # Scrollbar — чёрная рамка
        style.configure("Vertical.TScrollbar",
                        background=self.COLORS["border"],
                        troughcolor=self.COLORS["bg_panel"],
                        arrowcolor=self.COLORS["text_main"],
                        borderwidth=1,
                        relief="solid")
        style.map("Vertical.TScrollbar",
                  background=[("active", self.COLORS["accent_light"])])

        # Маленькие кнопки интервалов
        style.configure("Small.TButton",
                        background=self.COLORS["btn_small_bg"],
                        foreground=self.COLORS["text_main"],
                        font=("Segoe UI", 9),
                        borderwidth=0,
                        padding=[8, 4],
                        focuscolor="none")
        style.map("Small.TButton",
                  background=[("active", self.COLORS["btn_small_hover"]),
                              ("pressed", self.COLORS["btn_small_hover"])])

        # Кнопка «Заморозить» (синяя)
        style.configure("Freeze.TButton",
                        background=self.COLORS["btn_freeze_bg"],
                        foreground="white",
                        font=("Segoe UI", 9, "bold"),
                        borderwidth=0,
                        padding=[10, 5],
                        focuscolor="none")
        style.map("Freeze.TButton",
                  background=[("active", self.COLORS["btn_freeze_hover"]),
                              ("pressed", self.COLORS["btn_freeze_hover"])])

        # Кнопка «Разморозить» (оранжевая)
        style.configure("FreezeActive.TButton",
                        background=self.COLORS["btn_freeze_active_bg"],
                        foreground="white",
                        font=("Segoe UI", 9, "bold"),
                        borderwidth=0,
                        padding=[10, 5],
                        focuscolor="none")
        style.map("FreezeActive.TButton",
                  background=[("active", self.COLORS["btn_freeze_active_hover"]),
                              ("pressed", self.COLORS["btn_freeze_active_hover"])])

        # Контрастная кнопка «пыньк»
        style.configure("Contrast.TButton",
                        background=self.COLORS["btn_bg"],
                        foreground="#000000",
                        font=("Segoe UI", 11, "bold"),
                        borderwidth=0,
                        padding=[20, 10],
                        focuscolor="none")
        style.map("Contrast.TButton",
                  background=[("active", self.COLORS["btn_hover"]),
                              ("pressed", self.COLORS["btn_hover"])],
                  foreground=[("active", "#000000"),
                               ("pressed", "#000000")])
