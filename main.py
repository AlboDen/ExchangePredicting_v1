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

import matplotlib.pyplot as plt

if __name__ == '__main__':
    print("start")
    # app = Window()
    # shadowProcesses.RepeatedServerRequest.run()
    # ButtonHandlers()
    # app.mainloop()
    SAMPLE_VOLUME = 10
    MIN_NUMB_OF_SAMPLES = 10

    errors = np.array([])
    while True:
        print("Cycle #", len(errors))
        mass = BybitExchange.Klines.getIndexPrices()
        predicted = round(Statistic.BUILD_MODEL.buildModel(mass), 4)
        print("pred = ", predicted)
        time.sleep(5)
        fact = BybitExchange.Klines.get_current_price()
        print("next = ", fact)
        if fact-predicted <= -0.0001:
            errors = np.append(errors, fact-predicted)
        else:
            errors = np.append(errors, 0)

        print("errors = ", np.count_nonzero(errors)/len(errors))


