import statistics
import threading
from Calculations.statisticsMethods import Statistic
from network.BybitExchange import BybitExchange
from Bets.Bets import Bets

import time

class System:
    itSelf = None
    # sensLevels = None
    def __init__(self):
        self.assets = ["BTCUSDT", "XRPUSDT"]#,"ETHUSDT"]
        self.sensLevels = dict(zip(self.assets, [0.2, 0.00005]))

        self.assetSubSystems = []
        for i in self.assets:
            # print("assetSubSystems ",i)
            self.assetSubSystems.append(System.AssetSubSystem(i,self.sensLevels[i]))


    class AssetSubSystem:
        def __init__(self, asset, sensLevel):
            self.sensLevel = sensLevel

            self.asset = asset
            self.pastPriceValue = 0
            self.integroLaggedSubsystem = System.AssetSubSystem.integroLaggedSubsystem(asset=self.asset, sensLevel=self.sensLevel)

        class integroLaggedSubsystem:


            def __init__(self, asset, sensLevel):
                self.asset = asset
                self.sensLevel = sensLevel
                self.pastPriceValue = 0
                print("integroLaggedSubsystem ",self.asset)
                threading.Thread(target=self.cecker, daemon=True).start()

            def cecker(self):
                while True:
                    print("cecker ",self.asset," ",Bets.getBalance())
                    pastPriceValues = BybitExchange.Klines.getIndexPrices(symbol=self.asset, hours_back=4, interval=1)

                    integrateChangesIndecator = Statistic.TimeSeriesAnalisys.Indicators.check_changesIndicator(pastPriceValues) > self.sensLevel
                    predictedPriceValue = round(Statistic.BUILD_MODEL.buildModel(pastPriceValues), 4)

                    if self.pastPriceValue == 0:
                        self.pastPriceValue = predictedPriceValue
                    growthIndecator = predictedPriceValue > self.pastPriceValue

                    # default switch off trade block
                    returnBetFlag = False

                    # trade signals
                    # print("\tintegral signal: ", integrateChangesIndecator, " ", Statistic.TimeSeriesAnalisys.Indicators.check_changesIndicator(pastPriceValues))
                    # print("\tgrowth signal:   ", growthIndecator, " : \tpredicted =\t", predictedPriceValue, " fact = ", self.pastPriceValue)

                    if growthIndecator and integrateChangesIndecator:  # and changesIndecatorL:
                        Bets.createBet(BybitExchange.Klines.get_current_price(symbol=self.asset))
                        returnBetFlag = True

                    # await asyncio.sleep(3)  # неблокирующая пауза 3 сек
                    time.sleep(3)

                    factPriceValue = BybitExchange.Klines.get_current_price(symbol=self.asset)
                    # print("\t\t\t\t\t\t\t\tnext = \t\t", factPriceValue)
                    if returnBetFlag:
                        Bets.returnBet(factPriceValue)
                        returnBetFlag = False

                    self.pastPriceValue = factPriceValue


