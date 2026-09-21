import matplotlib.pyplot as plt
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from network.BybitExchange import BybitExchange


# from visual.window import Window
class Graph:
    class Orderbook:
        figure = Figure(figsize=(6, 4), dpi=100)
        canvas = None
        axes = None

        @staticmethod
        def initOrderbook(parantObject):
            Graph.Orderbook.axes = Graph.Orderbook.figure.add_subplot(111)
            # Graph.Orderbook.axes.plot([0,1,2,3], [10,22,30,12], 'o', color='blue', label=f'Bids')
            # Graph.Orderbook.axes.legend()

            Graph.Orderbook.canvas = FigureCanvasTkAgg(Graph.Orderbook.figure, master=parantObject)
            Graph.Orderbook.canvas.get_tk_widget().pack(
                fill=tk.BOTH,
                expand=True,
                # padx=5,
                # pady=5
            )
            Graph.Orderbook.figure.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.95)


        @staticmethod
        def _draw():
            """Внутренний метод — только для главного потока."""
            axes = Graph.Orderbook.axes
            axes.clear()
            axes.plot(BybitExchange.Orderbook.bidsPrice,
                BybitExchange.Orderbook.bidsSize,  'o', color='red', label='Bids')
            axes.plot(BybitExchange.Orderbook.asksPrice,
                BybitExchange.Orderbook.asksSize, 'o', color='green', label='Asks')
            axes.legend()
            axes.grid(True, linestyle='--', alpha=0.4)
            Graph.Orderbook.canvas.draw()
            print("draw")

            # return Graph.Orderbook.figure

        @staticmethod
        def reload():

            """
            Можно вызывать откуда угодно — из кнопки, из потока, из вебсокета.
            Отрисовка всегда уходит в главный поток через after().

            BybitExchange.Orderbook.bidsPrice,
            BybitExchange.Orderbook.bidsSize,
            BybitExchange.Orderbook.asksPrice,
            BybitExchange.Orderbook.asksSize
            """

            print("reloaded",BybitExchange.Orderbook.bidsPrice)
            root = Graph.Orderbook.canvas.get_tk_widget().winfo_toplevel()
            root.after(1, lambda: Graph.Orderbook._draw())
            print("view was updated")
        # @staticmethod
        # def reload(bidsPrice, bidsSize, asksPrice, asksSize):
        #     print("intered")
        #     axes = Graph.Orderbook.axes
        #     axes.clear()
        #
        #     axes.plot(bidsPrice, bidsSize, 'o', color='red', label=f'Bids')
        #     axes.plot(asksPrice, asksSize, 'o', color='green', label=f'Bids')
        #     axes.legend()
        #     # print("rewrite",super().__bases__.__name__)
        #     super().after(0,Graph.Orderbook.canvas.draw())
        #
        #     print("rewrite")


