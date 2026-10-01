import numpy as np
from scipy.stats import pearsonr
from Calculations.DataCombinations import DataCombinations
from Calculations.statisticsMethods import Statistic
from network.BybitExchange import BybitExchange
from network.DataBase.DataBaseManager import DataBaseManager
from shadowProcesses import shadowProcesses
from visual.buttonHandlers import ButtonHandlers
from visual.window import Window
import time
from Bets.Bets import Bets

import matplotlib.pyplot as plt
# if __name__ == '__main__':
#     db = DataBaseManager(db_path="./network/DataBase/black_box_laggsOnlyStrategy.db")
#     db.replace_save_time_with_bybit_time_all()

if __name__ == '__main__':
    print("start")
    # app = Window()
    # shadowProcesses.RepeatedServerRequest.run()
    # ButtonHandlers()
    # app.mainloop()

    Bets.toUpBalance_USDT(100000)

    db = DataBaseManager(db_path = "./network/DataBase/black_box_laggsOnlyStrategy.db")
    errors = np.array([])
    fact = 0
    while True:
        print("Cycle #", len(errors))
        mass = BybitExchange.Klines.getIndexPrices(symbol="ETHUSDT",hours_back=4,interval=1)
        # print("mass = ", mass)
        predicted = round(Statistic.BUILD_MODEL.buildModel(mass), 4)
        # print("pred = ", predicted, "np.mean(errors)*4 ", np.mean(errors)*10)
        if fact == 0:
            fact=predicted

        # target block№
        flag = False

        changesIndecator = Statistic.TimeSeriesAnalisys.Indicators.check_changesIndicator(mass) > 0.2
        changesIndecatorL = Statistic.TimeSeriesAnalisys.Indicators.check_changesIndicator(mass, depth = 4) > 10
        print("integ S", changesIndecator, " ",Statistic.TimeSeriesAnalisys.Indicators.check_changesIndicator(mass))
        print("integ L", changesIndecatorL, " ", Statistic.TimeSeriesAnalisys.Indicators.check_changesIndicator(mass, depth = 4))
        print("growth ",  predicted > fact, " : predicted = ", predicted, " fact = ", fact)
        if predicted > fact and changesIndecator:# and changesIndecatorL:
            flag = True
            c = BybitExchange.Klines.get_current_price(symbol="ETHUSDT")
            # print("pricvel = ", c)
            Bets.createBet(c)

        time.sleep(3)
        fact = BybitExchange.Klines.get_current_price(symbol="ETHUSDT")
        # print("postquel = ", fact)
        if flag:
            Bets.returnBet(fact)
            flag = False
        print("next = ", fact)
        if abs(fact-predicted) >= 10:
            errors = np.append(errors, 1)
        else:
            errors = np.append(errors, 0)
        # print("errors = ", np.count_nonzero(errors)/len(errors))


        db.save_prediction(
            table_name="xrp_predictions",              # имя таблицы — аргумент
            actual_price=fact,
            predicted_price=predicted,
            momentary_error = fact-predicted,
            accumulated_error = np.count_nonzero(errors)/len(errors),
            capital_growth = Bets.getBalance()
        )


