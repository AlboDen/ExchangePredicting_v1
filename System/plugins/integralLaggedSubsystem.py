import threading
import time

from PIL.ImageChops import difference

from System.plugins.__TEMPLATE__ import PLUGIN_TEMPLATE
from Bets.Bets import Bets
from Calculations.statisticsMethods import Statistic
from network.BybitExchange import BybitExchange


class integralLaggedSubsystem(PLUGIN_TEMPLATE):

    def __init__(self, asset, params = [], rightToMakeBet = False):
        self.stop_event = threading.Event()  # глобальный или в self
        self.inBetWaiting = False
        self.asset = asset
        self.params = params
        self.sensLevel = params[0]
        self.rightToMakeBet = rightToMakeBet
        self.pastPriceValue = 0
        # print("integralLaggedSubsystem ", self.asset)
        self._runChecker()

        self.capitagGain = 0
        self.errorsNumber = 0
        self.losses = 0

        self.EXIT_RATE = 0



    def cecker(self):
        while not self.stop_event.is_set():
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
                    self.inBetWaiting = True
                    Bets.createBet(curs=BybitExchange.Klines.get_current_price(symbol=self.asset), asset=self.asset)
                    returnBetFlag = True

            # await asyncio.sleep(3)  # неблокирующая пауза 3 сек

            time.sleep(3)

            factPriceValue = BybitExchange.Klines.get_current_price(symbol=self.asset)
            # print("\t\t\t\t\t\t\t\tnext = \t\t", factPriceValue)
            if returnBetFlag:
                difference = factPriceValue - self.pastPriceValue
                if difference < 0:
                    self.losses += difference
                    self.errorsNumber += 1
                self.capitagGain += difference

                Bets.returnBet(curs=factPriceValue, asset=self.asset, difference= difference)
                returnBetFlag = False
            self.pastPriceValue = factPriceValue
            self.inBetWaiting = False

    def _runChecker(self):
        self.thread = threading.Thread(target=self.cecker, daemon=True)
        self.thread.start()

    def _stopChecker(self):
        # print("THROAT STOPED")
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            if self.inBetWaiting:
                self.thread.join()
            else:
                self.thread.join(timeout=0)

    def exo(self) -> None:
        print("EXO of an asset ", self.asset, " integralLaggedSubsystem METHOD, params: ", self.params)

    def loadBasicParams(self):
        return {
            "sensitivityLevel": BybitExchange.Klines.get_current_price(symbol=self.asset)*0.00001,
        }
    def getParams(self, viewOfOutput = None):
        """to get setted parameters"""
        if viewOfOutput == None:
            return [self.sensLevel]
        if viewOfOutput == "dict":
            return {"sensitivityLevel":self.sensLevel}