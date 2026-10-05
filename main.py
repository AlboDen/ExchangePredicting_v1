import time

from ShadowProccesses.ShadowProccessesManager import ShadowProcessesManager
from System.System import System

if __name__ == '__main__':

    print("start screening abilities of grows")
    spm = ShadowProcessesManager()
    # print("start screening abilities of grows")
    time.sleep(3)
    # Bets.toUpBalance_USDT(100000)
    System.itSelf = System()
    try:
        while True:
            time.sleep(3)  # держим процесс живым
            System.itSelf.assetSubSystems["BTCUSDT"].methods[('integralLaggedSubsystem', '+00%')].exo()

    except KeyboardInterrupt:
        print("остановлено")