import time
import datetime
from ShadowProccesses.ShadowProccessesManager import ShadowProcessesManager
from System.System import System
from network.DataBase.plugins.capitalGainDB import CapitalGainDB
from network.DataBase.DataBaseManager import DataBaseManager
if __name__ == '__main__':

    print("start screening abilities of grows")
    ShadowProcessesManager.itSelf = ShadowProcessesManager()
    # print("start screening abilities of grows")
    time.sleep(3)
    # Bets.toUpBalance_USDT(100000)
    System.itSelf = System()
    DataBaseManager.itSelf = DataBaseManager(System.itSelf.settingFile.keys())

    # print("FFFFFFFFvalues ")

    DataBaseManager.itSelf.MethodsDataDB["BTCUSDT"].add_method(
        # exchange_time, parameters, method_name
        parameters=[14, 5],
        method_name="fff_meth"
    )
    DataBaseManager.itSelf.MethodsDataDB["XRPUSDT"].add_method(
        # exchange_time, parameters, method_name
        parameters=[14, 5],
        method_name="fff_meth"
    )
    DataBaseManager.itSelf.MethodsDataDB["ETHUSDT"].add_method(
        # exchange_time, parameters, method_name
        parameters=[14, 5],
        method_name="fff_meth"
    )
    System.itSelf.closeAllThreads()
    try:
        while True:
            print("...")

            time.sleep(3)  # держим процесс живым

            # System.itSelf.assetSubSystems["BTCUSDT"].methods[('integralLaggedSubsystem', '+00%')].exo()

    except KeyboardInterrupt:
        print("остановлено")