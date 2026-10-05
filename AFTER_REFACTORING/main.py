import time
from datetime import date

from AFTER_REFACTORING.System.System import System
from Bets.Bets import Bets
from AFTER_REFACTORING.DataBase.DataBaseManager import DataBaseManager

if __name__ == '__main__':
    print("start screening abilities of grows")

    Bets.toUpBalance_USDT(100000)
    System.itSelf = System()
    try:
        while True:
            time.sleep(1)  # держим процесс живым
    except KeyboardInterrupt:
        print("остановлено")