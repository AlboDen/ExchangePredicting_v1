import os
import threading

import numpy as np
from pybit.unified_trading import HTTP
from Calculations.statisticsMethods import Statistic
from network.DataBase.DataBaseManager import DataBaseManager
from visual.visualTablesDataInterface import VisualTablesInterface

class BybitExchange:
    session = HTTP(testnet=False)
    db_orderbook = DataBaseManager("./network/DataBase/orderbook.db")

    class Orderbook:
        currentAsset = None
        bidsPrice = []
        bidsSize = []
        asksPrice = []
        asksSize = []
        # if os.path.exists("./network/DataBase/orderbook.db"):
        #     os.remove("./network/DataBase/orderbook.db")
        #     print("Старая БД удалена")

        @staticmethod
        def getOrderbook(asset = "XRPUSDT"):
            BybitExchange.Orderbook.currentAsset = asset
            t = threading.Thread(target=BybitExchange.Orderbook.__getOrderbookInAdditionalThread, daemon=True)
            t.start()
            t.join()

        @staticmethod
        def __getOrderbookInAdditionalThread():
            # Этот метод работает в фоновом потоке — можно делать
            # долгие запросы к API, спать, читать файлы и т.п. иначе возникнет конфликт с потоком, отвечающим за tkinter
            response = BybitExchange.session.get_orderbook(
                category="spot",
                symbol=BybitExchange.Orderbook.currentAsset,
                limit=100,
            )

            bidsUnited = response["result"]['b']
            print(" bidsUnited ", len(bidsUnited),bidsUnited)
            BybitExchange.Orderbook.bidsPrice = []
            BybitExchange.Orderbook.bidsSize = []
            for i in bidsUnited:
                BybitExchange.Orderbook.bidsPrice.append(float(i[0]))
                BybitExchange.Orderbook.bidsSize.append(float(i[1]))
            asksUnited = response["result"]['a']
            BybitExchange.Orderbook.asksPrice = []
            BybitExchange.Orderbook.asksSize = []
            for i in asksUnited:
                BybitExchange.Orderbook.asksPrice.append(float(i[0]))
                BybitExchange.Orderbook.asksSize.append(float(i[1]))
            # print("BybitExchange.bidsPrice",BybitExchange.bidsPrice)

            BybitExchange.Orderbook.__fillDatabaseAfterServerRequest()
            BybitExchange.Orderbook.__updateVisualTables()
            print("data was updated",len(BybitExchange.Orderbook.asksPrice))

        @staticmethod
        def __fillDatabaseAfterServerRequest():
            BybitExchange.db_orderbook.insert_request(
                asks_prices=BybitExchange.Orderbook.asksPrice,
                asks_volumes=BybitExchange.Orderbook.asksSize,
                bids_prices=BybitExchange.Orderbook.bidsPrice,
                bids_volumes=BybitExchange.Orderbook.bidsSize,
                spread=np.min(BybitExchange.Orderbook.asksPrice)-np.max(BybitExchange.Orderbook.bidsPrice),
                regression_area_ratio=None,
                rectangle_area_ratio=0.98,
                regression_coeff_ratio=1.05,
                points_above_regression_ratio=0.42,
                asks_third1_count=1,
                asks_third2_count=1,
                asks_third3_count=1,
                bids_third1_count=1,
                bids_third2_count=1,
                bids_third3_count=1,

                # динамические параметры по срокам (если нужны)
                short_term_params={
                    "spread": 0.65,
                    "regression_area_ratio": 1.12,
                    "equilibrium_price_growth_ratio": 0.03,
                    "open_price_growth_ratio": 0.02,
                },
                medium_term_params={
                    "spread": 0.72,
                    "regression_area_ratio": 1.18,
                    "equilibrium_price_growth_ratio": 0.05,
                    "close_price_growth_ratio": 0.04,
                },
                long_term_params=None  # можно не передавать, если нет данных
            )

        @staticmethod
        def __updateVisualTables():
            VisualTablesInterface.itSelf.static_set("Спрэд", "bids", "0.0234")
            # VisualTablesInterface.itSelf.static_set("Спрэд", "bids", "0.0234")
            VisualTablesInterface.itSelf.static_set_color("Спрэд", "#FF0000")