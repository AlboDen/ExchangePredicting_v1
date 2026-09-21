from network.BybitExchange import BybitExchange
from visual.graph import Graph
import time

class ButtonHandlers:
    @staticmethod
    def staffButtonHandler():
        print("butt pressed")
        BybitExchange.Orderbook.getOrderbook()
        print("FIX ended")
        Graph.Orderbook.reload()

        print("butt unpressed")
