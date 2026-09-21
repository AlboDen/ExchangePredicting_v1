import tkinter as tk
from tkinter import ttk
import math

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from network.BybitExchange import BybitExchange
from visual.buttonHandlers import ButtonHandlers
from visual.graph import Graph


class StackedWidget(tk.Frame):
    """Простая реализация StackedWidget: хранит фреймы и показывает только один."""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._frames = {}
        self.current_name = None

    def add(self, name, frame):
        self._frames[name] = frame
        frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        frame.lift()

    def set_current(self, name):
        if name not in self._frames:
            raise ValueError(f"Нет фрейма с именем {name}")
        self._frames[name].lift()
        self.current_name = name

    def get_current(self):
        return self.current_name


class Window(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("График в окне Python")
        self.geometry("1000x600")
        self.minsize(700, 400)

        # Контейнер, в котором можно менять размер панелей мышью
        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Левая панель — график
        graph_frame = ttk.Frame(paned_window, padding=5)
        paned_window.add(graph_frame, weight=4)

        # Текстовый лейбл на graph_frame
        self.info_label = tk.Label(
            graph_frame,
            text="Информация о стакане",
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        self.info_label.pack(fill=tk.X, pady=(0, 5))

        # StackedWidget под лейблом
        self.stacked_widget = StackedWidget(graph_frame)
        self.stacked_widget.pack(fill=tk.BOTH, expand=True)

        # Страница 1 — сам график (сюда initOrderbook положит canvas)
        graph_page = tk.Frame(self.stacked_widget)
        self.stacked_widget.add("graph", graph_page)
        self.stacked_widget.set_current("graph")

        # Страница 2 — заглушка (например, для логов или доп. информации)
        log_page = tk.Frame(self.stacked_widget)
        tk.Label(log_page, text="Здесь могут быть логи или доп. данные",
                 font=("Arial", 11)).pack(pady=20)
        self.stacked_widget.add("logs", log_page)

        # График рисуется на странице "graph"
        Graph.Orderbook.initOrderbook(graph_page)

        # Правая панель — управление
        control_frame = ttk.Frame(paned_window, padding=15)
        paned_window.add(control_frame, weight=1)

        # Кнопка переключения страниц (для примера)
        ttk.Button(
            control_frame,
            text="График",
            command=lambda: self.stacked_widget.set_current("graph")
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            control_frame,
            text="Логи",
            command=lambda: self.stacked_widget.set_current("logs")
        ).pack(fill=tk.X, pady=2)

        # button
        ttk.Button(
            control_frame,
            text="пыньк",
            command=ButtonHandlers.staffButtonHandler
        ).pack()
