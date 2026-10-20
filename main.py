import time
import datetime
from ShadowProccesses.ShadowProccessesManager import ShadowProcessesManager
from System.System import System
from Bets.Bets import Bets
from network import BybitExchange
from network.BybitExchange import BybitExchange
from network.plugins.BybitSpotLimiter import BybitSpotLimiter
from pybit.unified_trading import HTTP
from network.DataBase.plugins.capitalGainDB import CapitalGainDB
from network.DataBase.DataBaseManager import DataBaseManager
#testnet Bn8zZbAlIG2gRLPaAg hMnOLyoh4vQjJbQMeNFlxUutTptMIANUFIXy
# NORM testnet ZotNYzW49ASjZuIM6f YWVdQ7iYhnZmIn7lzx1wq3QdVy8FzA8CX5E0

if __name__ == '__main__':
    print("start screening abilities of grows")
    ShadowProcessesManager.itSelf = ShadowProcessesManager()
    time.sleep(10)
    Bets.toUpBalance_USDT(10000)
    System.switch_printingEraRaport()
    System.itSelf = System()

    DataBaseManager.itSelf = DataBaseManager(System.itSelf.settingFile.keys())
    System.runCheckers()
    try:
        counterOfEras = 1
        while True:
            print("ERA #", counterOfEras)
            time.sleep(300)  # держим процесс живым№
            System.forsedPutSystem()
            del DataBaseManager.itSelf
            del System.itSelf
            System.itSelf = System()
            DataBaseManager.itSelf = DataBaseManager(System.itSelf.settingFile.keys())
            System.runCheckers()
            counterOfEras += 1
    except KeyboardInterrupt:
        print("остановлено")
#requests.exceptions.ReadTimeout: HTTPSConnectionPool(host='api.bybit.com', port=443): Read timed out. (read timeout=10)

#urllib3.exceptions.ProtocolError: ('Connection aborted.', ConnectionResetError(10054, 'Удаленный хост принудительно разорвал существующее подключение', None, 10054, None))
# During handling of the above exception, another exception occurred:
#requests.exceptions.ConnectionError: ('Connection aborted.', ConnectionResetError(10054, 'Удаленный хост принудительно разорвал существующее подключение', None, 10054, None))

#Ошибка запроса к Bybit в getIndexPrices: HTTPSConnectionPool(host='api.bybit.com', port=443): Read timed out. (read timeout=10)Exception in thread Thread-2339 (cecker):

#RETURN BET  BTCUSDT 14.56605983523345

# endpoint="https://api-testnet.bybit.com",  # это именно тестовая сеть (testnet)
#
# resp = BybitExchange.BybitSpotLimiter.place_limit_order("XRPUSDT", "Buy", 0.001, 42000)
#
# # trader.place_limit_order("BTCUSDT", "Buy", 0.001, 42000)
# order_id = resp["result"]["orderId"]
# print("Ордер создан, ID:", order_id)+

