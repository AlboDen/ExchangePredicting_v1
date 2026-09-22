import time

import matplotlib.pyplot as plt
import tkinter as tk

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from network.BybitExchange import BybitExchange
from Calculations.statisticsMethods import Statistic
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
                      BybitExchange.Orderbook.bidsSize,  'o', color='red', label=f'Bids {len(BybitExchange.Orderbook.bidsSize)}')
            axes.plot(BybitExchange.Orderbook.asksPrice,
                      BybitExchange.Orderbook.asksSize, 'o', color='green', label=f'Asks {len(BybitExchange.Orderbook.asksPrice)}')
            axes.legend()

            max_x = np.max(BybitExchange.Orderbook.bidsPrice)
            min_x = np.min(BybitExchange.Orderbook.asksPrice)
            mid_x = (min_x + max_x) / 2
            axes.axvline(mid_x, color='green', linestyle='--', alpha=0.7)
            Graph.Orderbook.drawRegressionLine(BybitExchange.Orderbook.bidsPrice, BybitExchange.Orderbook.bidsSize)
            Graph.Orderbook.drawRegressionLine(BybitExchange.Orderbook.asksPrice, BybitExchange.Orderbook.asksSize)

            # axes.grid(True, linestyle='--', alpha=0.4)
            Graph.Orderbook.canvas.draw()



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


            root = Graph.Orderbook.canvas.get_tk_widget().winfo_toplevel()
            root.after(1, lambda: Graph.Orderbook._draw())

            Statistic.StaticAnalisys.areaUnderLine_bids,Statistic.StaticAnalisys.points_above_regression_bids = Graph.Orderbook.drawRegressionLine(BybitExchange.Orderbook.bidsPrice, BybitExchange.Orderbook.bidsSize)
            Statistic.StaticAnalisys.areaUnderLine_asks,Statistic.StaticAnalisys.points_above_regression_asks = Graph.Orderbook.drawRegressionLine(BybitExchange.Orderbook.asksPrice, BybitExchange.Orderbook.asksSize)


        @staticmethod
        def drawRegressionLine(x_presetted, y_presetted):
            _, x, y, areaUnderLine, points_above_regression = Statistic.Regressions.calculateRegressionNumbers(x_presetted, y_presetted)

            Graph.Orderbook.axes.plot(x,y, color='black', linewidth=2,  label=f'Asks apps')
            Graph.Orderbook.canvas.draw()

            return areaUnderLine, points_above_regression

