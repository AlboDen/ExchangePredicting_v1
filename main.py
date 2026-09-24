import numpy as np

from Calculations.DataCombinations import DataCombinations
from Calculations.statisticsMethods import Statistic
from network.DataBase.DataBaseManager import DataBaseManager
from shadowProcesses import shadowProcesses
from visual.buttonHandlers import ButtonHandlers
from visual.window import Window

import matplotlib.pyplot as plt

if __name__ == '__main__':
    print("start")
    # app = Window()
    # shadowProcesses.RepeatedServerRequest.run()
    # ButtonHandlers()
    # app.mainloop()


    db = DataBaseManager("C:/Users/Alex_/PycharmProjects/PythonProject1/network/DataBase/orderbook.db")
    # print("calc", )
    # print("finish", db.get_history_columns(["request_time"]))
    DataCombinations(db)
    # print(DataCombinations.params_1_power)



    d = {
        # "rectangle_area_ratio**6         ": np.array(db.get_history_columns(["rectangle_area_ratio"])[
        #     "rectangle_area_ratio"])**6,
        # "points_above_regression_ratio": db.get_history_columns(["points_above_regression_ratio"])[
        #     "points_above_regression_ratio"],
        # "asks_third1_count            ": db.get_history_columns(["asks_third1_count"])[
        #     "asks_third1_count"],
        "asks_third2_count            ": db.get_history_columns(["asks_third2_count"])[
            "asks_third2_count"],
        "asks_third3_count            ": 1.69-np.array(db.get_history_columns(["asks_third3_count"])["asks_third3_count"])**3*0.07
        # "bids_third1_count            ": db.get_history_columns(["bids_third1_count"])[
        #     "bids_third1_count"],
        # "bids_third2_count            ": db.get_history_columns(["bids_third2_count"])[
        #     "bids_third2_count"],
        # "bids_third3_count            ": db.get_history_columns(["bids_third3_count"])[
        #     "bids_third3_count"],
        # "asks_third1_count**2             ":
        #           np.array(db.get_history_columns(["asks_third1_count"])[
        #                        "asks_third1_count"]) ** 2,
        #       "asks_third2_count**2             ":
        #           np.array(db.get_history_columns(["asks_third2_count"])[
        #                        "asks_third2_count"]) ** 2,
        #       "asks_third3_count**2             ":
        #           np.array(db.get_history_columns(["asks_third3_count"])[
        #                        "asks_third3_count"]) ** 2,
        #       "bids_third1_count**2          ":
        #           np.array(db.get_history_columns(["bids_third1_count"])[
        #                        "bids_third1_count"]) ** 2,
        #       "bids_third2_count**2          ":
        #           np.array(db.get_history_columns(["bids_third2_count"])[
        #                        "bids_third2_count"]) ** 2,
        #       "bids_third3_count**2           ":
        #           np.array(db.get_history_columns(["bids_third3_count"])[
        #                        "bids_third3_count"]) ** 2,
        # "asks_third1_count**3             ":
        #     np.array(db.get_history_columns(["asks_third1_count"])[
        #                  "asks_third1_count"]) ** 3,
        # "asks_third2_count**3             ":
        #     np.array(db.get_history_columns(["asks_third2_count"])[
        #                  "asks_third2_count"]) ** 3,
        # "asks_third3_count**3             ":
        #     np.array(db.get_history_columns(["asks_third3_count"])[
        #                  "asks_third3_count"]) ** 3,
        # "asks_third3_count**4             ":
        #     np.array(db.get_history_columns(["asks_third3_count"])[
        #                  "asks_third3_count"]) ** 4,
        # "asks_third3_count**5             ":
        #     np.array(db.get_history_columns(["asks_third3_count"])[
        #                  "asks_third3_count"]) ** 5,
        # "asks_third3_count**6             ":
        #     np.array(db.get_history_columns(["asks_third3_count"])[
        #                  "asks_third3_count"]) ** 6,
        # "bids_third1_count**3          ":
        #     np.array(db.get_history_columns(["bids_third1_count"])[
        #                  "bids_third1_count"]) ** 3,
        # "bids_third2_count**3          ":
        #     np.array(db.get_history_columns(["bids_third2_count"])[
        #                  "bids_third2_count"]) ** 3,
        # "bids_third3_count**3           ":
        #     np.array(db.get_history_columns(["bids_third3_count"])[
        #                  "bids_third3_count"]) ** 3



    }
    Statistic.TimeSeriesAnalisys.print_correlation_matrix_with_y(db.get_actual_prices(), d, "actual Price")

    # y = 1.670 - 0.002*rectangle_area_ratio          + 0.002*points_above_regression_ratio + 0.017*asks_third2_count             - 0.069*asks_third3_count
    print("lll",db.get_history_columns(["asks_third3_count"]))
    y = 1.69 - 0.07*np.array(db.get_history_columns(["asks_third3_count"])["asks_third3_count"])
    DataCombinations.plot_all_features_vs_y(db.get_actual_prices(), d)

    # k =Statistic.TimeSeriesAnalisys.best_regression(db.get_actual_prices(), d)
    # print("finish",k["r2"], k["equation"])
