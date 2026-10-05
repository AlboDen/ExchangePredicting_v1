import json
import os
import time
from datetime import date

from AFTER_REFACTORING.ShadowProccesses.ShadowProccessesManager import ShadowProcessesManager
from AFTER_REFACTORING.System.System import System
from Bets.Bets import Bets
from AFTER_REFACTORING.DataBase.DataBaseManager import DataBaseManager

if __name__ == '__main__':

    print("start screening abilities of grows")
    spm = ShadowProcessesManager()
    print("start screening abilities of grows")
    time.sleep(3)
    # Bets.toUpBalance_USDT(100000)
    System.itSelf = System()
    try:
        while True:
            time.sleep(3)  # держим процесс живым
            System.itSelf.assetSubSystems["BTCUSDT"].methods[('integralLaggedSubsystem', '+00%', '+00%')].exo()

    except KeyboardInterrupt:
        print("остановлено")