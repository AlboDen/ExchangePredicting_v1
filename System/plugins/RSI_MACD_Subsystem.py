import time

from System.plugins.__TEMPLATE__ import PLUGIN_TEMPLATE
import threading


class RSI_MACD_Subsystem(PLUGIN_TEMPLATE):
    def __init__(self, asset, params = [], rightToMakeBet = False):
        self.activeBalance_shadowAsset_USDT = 0
        self.stop_event = threading.Event()  # глобальный или в self
        self.inBetWaiting = False
        self.asset = asset
        self.params = params
        self.sensLevel = params[0]
        self.sensLevel1 = params[1]
        print("LLLLLLLLLLLLLLLLLLLLLLLLLLLL",params)
        self.rightToMakeBet = rightToMakeBet
        self.pastPriceValue = 0
        # print("integralLaggedSubsystem ", self.asset)
        self._runChecker()

        self.capitagGain = 0
        self.errorsNumber = 0
        self.losses = 0

        self.EXIT_RATE = 0

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

    def cecker(self):
        while not self.stop_event.is_set():
            # print("ffff",self.params)
            time.sleep(1)
            # pass

    def exo(self) -> None:
        """print privet asset information"""
        """this need to check workability of the class"""
        pass

    @staticmethod
    def loadBasicParams(asset= None):
        if asset != None:
            return {
                "GGG": 0.00001,
            }
        else:
            return {
                "GGG": 404,
            }

    def getParams(self,viewOfOutput = None) -> list:

        if viewOfOutput == None:
            return self.params
        if viewOfOutput == "dict":
            return {"GGG":self.sensLevel,
                    "GGG1":self.sensLevel1}
