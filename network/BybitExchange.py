import os
import threading

import numpy as np
from pybit.unified_trading import HTTP
from Calculations.statisticsMethods import Statistic
from network.DataBase.DataBaseManager import DataBaseManager
from visual.visualTablesDataInterface import VisualTablesInterface

class BybitExchange:
    session = HTTP(testnet=False)
    DataBaseManager.itSelf = DataBaseManager("./network/DataBase/orderbook.db")

    class Orderbook:
        currentAsset = None
        bidsPrice = []
        bidsSize = []
        asksPrice = []
        asksSize = []
        currentOrderbookParams = None
        # if os.path.exists("./network/DataBase/orderbook.db"):
        #     os.remove("./network/DataBase/orderbook.db")

        @staticmethod
        def getOrderbook(asset = "XRPUSDT"):
            BybitExchange.Orderbook.currentAsset = asset
            t = threading.Thread(target=BybitExchange.Orderbook.__getOrderbookInAdditionalThread, daemon=True)
            t.start()
            t.join()


        # @staticmethod
        # def __getOrderbookInAdditionalThread():

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

            BybitExchange.Orderbook.currentOrderbookParams = Statistic.StaticAnalisys.calculateParams(
                BybitExchange.Orderbook.bidsPrice,
                BybitExchange.Orderbook.bidsSize,
                BybitExchange.Orderbook.asksPrice,
                BybitExchange.Orderbook.asksSize
                )
            # print("CHECK PARAMS:\t\t", BybitExchange.Orderbook.currentOrderbookParams)#[""])

            BybitExchange.Orderbook.__fillDatabaseAfterServerRequest()
            BybitExchange.Orderbook.__updateVisualTables()



        @staticmethod
        def __fillDatabaseAfterServerRequest():
            DataBaseManager.itSelf.insert_request(
                asks_prices=BybitExchange.Orderbook.asksPrice,
                asks_volumes=BybitExchange.Orderbook.asksSize,
                bids_prices=BybitExchange.Orderbook.bidsPrice,
                bids_volumes=BybitExchange.Orderbook.bidsSize,
                spread=np.min(BybitExchange.Orderbook.asksPrice)-np.max(BybitExchange.Orderbook.bidsPrice),
                regression_area_ratio=BybitExchange.Orderbook.currentOrderbookParams["regression_area_ratio"],
                rectangle_area_ratio=BybitExchange.Orderbook.currentOrderbookParams["rectangle_area_ratio"],
                regression_coeff_ratio=BybitExchange.Orderbook.currentOrderbookParams["regression_coeff_ratio"],
                points_above_regression_ratio=BybitExchange.Orderbook.currentOrderbookParams["points_above_regression_ratio"],
                asks_third1_count=BybitExchange.Orderbook.currentOrderbookParams["asks_third1_count"],
                asks_third2_count=BybitExchange.Orderbook.currentOrderbookParams["asks_third2_count"],
                asks_third3_count=BybitExchange.Orderbook.currentOrderbookParams["asks_third3_count"],
                bids_third1_count=BybitExchange.Orderbook.currentOrderbookParams["bids_third1_count"],
                bids_third2_count=BybitExchange.Orderbook.currentOrderbookParams["bids_third2_count"],
                bids_third3_count=BybitExchange.Orderbook.currentOrderbookParams["bids_third3_count"],

                # динамические параметры по срокам (если нужны)
                short_term_params={
                    "spread":                       BybitExchange.Orderbook.currentOrderbookParams["short_term_params"]["spread"],
                    "regression_area_ratio":        BybitExchange.Orderbook.currentOrderbookParams["short_term_params"]["regression_area_ratio"],
                    "rectangle_area_ratio":         BybitExchange.Orderbook.currentOrderbookParams["short_term_params"]["rectangle_area_ratio"],
                    "regression_coeff_ratio":       BybitExchange.Orderbook.currentOrderbookParams["short_term_params"]["regression_coeff_ratio"],
                    "points_above_regression_ratio":BybitExchange.Orderbook.currentOrderbookParams["short_term_params"]["points_above_regression_ratio"],
                    "asks_third1_count":            BybitExchange.Orderbook.currentOrderbookParams["short_term_params"]["asks_third1_count"],
                    "asks_third2_count":            BybitExchange.Orderbook.currentOrderbookParams["short_term_params"]["asks_third2_count"],
                    "asks_third3_count":            BybitExchange.Orderbook.currentOrderbookParams["short_term_params"]["asks_third3_count"],
                    "bids_third1_count":            BybitExchange.Orderbook.currentOrderbookParams["short_term_params"]["bids_third1_count"],
                    "bids_third2_count":            BybitExchange.Orderbook.currentOrderbookParams["short_term_params"]["bids_third2_count"],
                    "bids_third3_count":            BybitExchange.Orderbook.currentOrderbookParams["short_term_params"]["bids_third3_count"],

                    # "equilibrium_vector_magnitude_growth_ratio": BybitExchange.Orderbook.currentOrderbookParams["short_term_params"]["equilibrium_vector_magnitude_growth_ratio"],
                    # "equilibrium_price_growth_ratio": BybitExchange.Orderbook.currentOrderbookParams["short_term_params"]["equilibrium_price_growth_ratio"],
                    #
                    # "open_price_growth_ratio":      BybitExchange.Orderbook.currentOrderbookParams["short_term_params"]["open_price_growth_ratio"],
                },
                medium_term_params={
                    "spread":                       BybitExchange.Orderbook.currentOrderbookParams["medium_term_params"]["spread"],
                    "regression_area_ratio":        BybitExchange.Orderbook.currentOrderbookParams["medium_term_params"]["regression_area_ratio"],
                    "rectangle_area_ratio":         BybitExchange.Orderbook.currentOrderbookParams["medium_term_params"]["rectangle_area_ratio"],
                    "regression_coeff_ratio":       BybitExchange.Orderbook.currentOrderbookParams["medium_term_params"]["regression_coeff_ratio"],
                    "points_above_regression_ratio":BybitExchange.Orderbook.currentOrderbookParams["medium_term_params"]["points_above_regression_ratio"],
                    "asks_third1_count":            BybitExchange.Orderbook.currentOrderbookParams["medium_term_params"]["asks_third1_count"],
                    "asks_third2_count":            BybitExchange.Orderbook.currentOrderbookParams["medium_term_params"]["asks_third2_count"],
                    "asks_third3_count":            BybitExchange.Orderbook.currentOrderbookParams["medium_term_params"]["asks_third3_count"],
                    "bids_third1_count":            BybitExchange.Orderbook.currentOrderbookParams["medium_term_params"]["bids_third1_count"],
                    "bids_third2_count":            BybitExchange.Orderbook.currentOrderbookParams["medium_term_params"]["bids_third2_count"],
                    "bids_third3_count":            BybitExchange.Orderbook.currentOrderbookParams["medium_term_params"]["bids_third3_count"],
                    # "equilibrium_price_growth_ratio": BybitExchange.Orderbook.currentOrderbookParams["medium_term_params"]["equilibrium_price_growth_ratio"],
                    # "open_price_growth_ratio":      BybitExchange.Orderbook.currentOrderbookParams["medium_term_params"]["open_price_growth_ratio"],
                },
                long_term_params={
                    "spread":                       BybitExchange.Orderbook.currentOrderbookParams["long_term_params"]["spread"],
                    "regression_area_ratio":        BybitExchange.Orderbook.currentOrderbookParams["long_term_params"]["regression_area_ratio"],
                    "rectangle_area_ratio":         BybitExchange.Orderbook.currentOrderbookParams["long_term_params"]["rectangle_area_ratio"],
                    "regression_coeff_ratio":       BybitExchange.Orderbook.currentOrderbookParams["long_term_params"]["regression_coeff_ratio"],
                    "points_above_regression_ratio":BybitExchange.Orderbook.currentOrderbookParams["long_term_params"]["points_above_regression_ratio"],
                    "asks_third1_count":            BybitExchange.Orderbook.currentOrderbookParams["long_term_params"]["asks_third1_count"],
                    "asks_third2_count":            BybitExchange.Orderbook.currentOrderbookParams["long_term_params"]["asks_third2_count"],
                    "asks_third3_count":            BybitExchange.Orderbook.currentOrderbookParams["long_term_params"]["asks_third3_count"],
                    "bids_third1_count":            BybitExchange.Orderbook.currentOrderbookParams["long_term_params"]["bids_third1_count"],
                    "bids_third2_count":            BybitExchange.Orderbook.currentOrderbookParams["long_term_params"]["bids_third2_count"],
                    "bids_third3_count":            BybitExchange.Orderbook.currentOrderbookParams["long_term_params"]["bids_third3_count"],
                    # "equilibrium_price_growth_ratio": BybitExchange.Orderbook.currentOrderbookParams["long_term_params"]["equilibrium_price_growth_ratio"],
                    # "open_price_growth_ratio":      BybitExchange.Orderbook.currentOrderbookParams["long_term_params"]["open_price_growth_ratio"],
                },
            )

        @staticmethod
        def __updateVisualTables():
            VisualTablesInterface.itSelf.static_set("Спрэд", "bids", "0.0234")
            # VisualTablesInterface.itSelf.static_set("Спрэд", "bids", "0.0234")
            VisualTablesInterface.itSelf.static_set_color("Спрэд", "#FF0000")