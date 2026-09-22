import threading

from pybit.unified_trading import HTTP

from network.DataBase.DataBaseManager import DataBaseManager
from visual.tablesInterface import TablesInterface


class BybitExchange:
    session = HTTP(testnet=False)


    class Orderbook:
        currentAsset = None
        bidsPrice = []
        bidsSize = []
        asksPrice = []
        asksSize = []
        db = DataBaseManager.OrderbookDatabase()

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
            print("data was updated",len(BybitExchange.Orderbook.asksPrice))

        @staticmethod
        def __fillDatabaseAfterServerRequest():
            BybitExchange.db.fill_database_in_background(raw_asks_prices = BybitExchange.Orderbook.asksPrice,
                raw_asks_sizes = BybitExchange.Orderbook.asksSize,
                raw_bids_prices = BybitExchange.Orderbook.bidsPrice,
                raw_bids_sizes = BybitExchange.Orderbook.bidsSize)

            # TablesInterface.db.connect()
            # TablesInterface.db.clear_tables()
            # TablesInterface.db.create_all()
            #
            # # Точки
            # raw_asks_id = TablesInterface.db.insert_points("raw_asks", [BybitExchange.Orderbook.asksPrice, BybitExchange.Orderbook.asksSize])
            # raw_bids_id = TablesInterface.db.insert_points("raw_bids", [BybitExchange.Orderbook.bidsPrice, BybitExchange.Orderbook.bidsSize])
            # print("[BybitExchange.Orderbook.asksPrice, BybitExchange.Orderbook.asksSize]",[BybitExchange.Orderbook.asksPrice, BybitExchange.Orderbook.asksSize])
            # # Связать всё
            # req_id = TablesInterface.db.insert_request(
            #     raw_asks_id=raw_asks_id, raw_bids_id=raw_bids_id,
            # )
            # TablesInterface.db.close()