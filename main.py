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
if __name__ == '__main__':

    print("start screening abilities of grows")
    ShadowProcessesManager.itSelf = ShadowProcessesManager()
    time.sleep(10)
    Bets.toUpBalance_USDT(10000)
    # System.switch_printingEraRaport()
    System.itSelf = System()

    DataBaseManager.itSelf = DataBaseManager(System.itSelf.settingFile.keys())
    System.runCheckers()
    try:
        counterOfEras = 1
        while True:
            print("ERA #", counterOfEras)
            time.sleep(3)  # держим процесс живым№
            System.forsedPutSystem()
            del DataBaseManager.itSelf
            del System.itSelf
            System.itSelf = System()
            DataBaseManager.itSelf = DataBaseManager(System.itSelf.settingFile.keys())
            System.runCheckers()
            counterOfEras += 1
    except KeyboardInterrupt:
        print("остановлено")
