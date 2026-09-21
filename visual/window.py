import tkinter as tk
from tkinter import ttk
import math

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from network.BybitExchange import BybitExchange
from visual.buttonHandlers import ButtonHandlers
from visual.graph import Graph


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
        Graph.Orderbook.initOrderbook(graph_frame)

        # Правая панель — управление
        control_frame = ttk.Frame(paned_window, padding=15)
        paned_window.add(control_frame, weight=1)



        # button
        ttk.Button(
            control_frame,
            text="пыньк",
            command = ButtonHandlers.staffButtonHandler
        ).pack()

