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
        self.sensLevel = 1
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

    def cecker(self, data: list) -> dict:
        print("ffff")
        time.sleep(1)
        # pass

    def exo(self) -> None:
        """print privet asset information"""
        """this need to check workability of the class"""
        pass

    def loadBasicParams(self):
        return {
            "eee": 222
        }

    def getParams(self) -> list:
        """to get setted parameters"""
        pass
