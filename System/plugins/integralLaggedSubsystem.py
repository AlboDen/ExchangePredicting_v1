import threading
import time

from System.plugins.__TEMPLATE__ import PLUGIN_TEMPLATE
from Bets.Bets import Bets
from Calculations.statisticsMethods import Statistic
from network.BybitExchange import BybitExchange


class integralLaggedSubsystem(PLUGIN_TEMPLATE):

    def __init__(self, asset, params = [], rightToMakeBet = False):
        self.asset = asset
        self.params = params
        self.sensLevel = params[0]
        self.rightToMakeBet = rightToMakeBet
        self.pastPriceValue = 0
        # print("integralLaggedSubsystem ", self.asset)
        self._runChecker()



    def cecker(self):
        while True:
            # print("cecker ",self.asset," ",Bets.getBalance())
            pastPriceValues = BybitExchange.Klines.getIndexPrices(symbol=self.asset, hours_back=4, interval=1)

            integrateChangesIndecator = Statistic.TimeSeriesAnalisys.Indicators.check_changesIndicator(
                pastPriceValues) > self.sensLevel
            predictedPriceValue = round(Statistic.BUILD_MODEL.buildModel(pastPriceValues), 4)

            if self.pastPriceValue == 0:
                self.pastPriceValue = predictedPriceValue
            growthIndecator = predictedPriceValue > self.pastPriceValue

            # default switch off trade block
            returnBetFlag = False

            # trade signals
            if self.rightToMakeBet:
                # print("asset",self.asset)
                # print("\tintegral signal: ", integrateChangesIndecator, " ", Statistic.TimeSeriesAnalisys.Indicators.check_changesIndicator(pastPriceValues))
                # print("\tgrowth signal:   ", growthIndecator, " : \tpredicted =\t", predictedPriceValue, " fact = ", self.pastPriceValue,"\tdiff =",predictedPriceValue-self.pastPriceValue)
                pass

            if growthIndecator and integrateChangesIndecator:  # and changesIndecatorL:
                if self.rightToMakeBet:
                    Bets.createBet(curs=BybitExchange.Klines.get_current_price(symbol=self.asset), asset=self.asset)
                    returnBetFlag = True

            # await asyncio.sleep(3)  # неблокирующая пауза 3 сек

            time.sleep(3)

            factPriceValue = BybitExchange.Klines.get_current_price(symbol=self.asset)
            # print("\t\t\t\t\t\t\t\tnext = \t\t", factPriceValue)
            if returnBetFlag:
                Bets.returnBet(curs=factPriceValue, asset=self.asset, difference= factPriceValue - self.pastPriceValue)
                returnBetFlag = False
            self.pastPriceValue = factPriceValue

    def _runChecker(self):
        self.thread = threading.Thread(target=self.cecker, daemon=True)
        self.thread.start()

    def _stopChecker(self):
        if self.thread and self.thread.is_alive():
            self.thread.join()

    def exo(self) -> None:
        print("EXO of an asset ", self.asset, " integralLaggedSubsystem METHOD, params: ", self.params)

    def loadBasicParams(self):
        return {
            "sensitivityLevel": BybitExchange.Klines.get_current_price(symbol=self.asset)*0.00001,
        }