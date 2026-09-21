import threading

from pybit.unified_trading import HTTP

class BybitExchange:
    session = HTTP(testnet=False)
    class Orderbook:
        currentAsset = None
        bidsPrice = []
        bidsSize = []
        asksPrice = []
        asksSize = []

        @staticmethod
        def getOrderbook(asset = "BTCUSD"):
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
                limit=3000,
            )

            bidsUnited = response["result"]['a']

            BybitExchange.Orderbook.bidsPrice = []
            BybitExchange.Orderbook.bidsSize = []
            for i in bidsUnited:
                BybitExchange.Orderbook.bidsPrice.append(i[0])
                BybitExchange.Orderbook.bidsSize.append(i[1])
            asksUnited = response["result"]['b']
            BybitExchange.Orderbook.asksPrice = []
            BybitExchange.Orderbook.asksSize = []
            for i in asksUnited:
                BybitExchange.Orderbook.asksPrice.append(i[0])
                BybitExchange.Orderbook.asksSize.append(i[1])
            # print("BybitExchange.bidsPrice",BybitExchange.bidsPrice)
            print("data was updated")