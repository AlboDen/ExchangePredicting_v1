from network.DataBase import DataBaseManager
from network.DataBase.DataBaseManager import DataBaseManager


class Bets:
    balance_USDT = 0

    activeBalance = {}

    @staticmethod
    def toUpBalance_USDT(payment):
        Bets.balance_USDT += payment

    @staticmethod
    def calculateAvailableAmountToBet():
        if Bets.balance_USDT > 5000:
            return Bets.balance_USDT*0.1
        return 0

    @staticmethod
    def createBet(curs,asset,rightToMakeBet = False):
        if rightToMakeBet:
            print("CREATING BET ",asset)
            availableAmount = Bets.calculateAvailableAmountToBet()

            Bets.balance_USDT -= availableAmount
            # if Bets.activeBalance[asset].if_exist():
            #     Bets.balance_USDT += availableAmount
            try:
                Bets.activeBalance[asset] += availableAmount * (1/curs)
            except KeyError:
                Bets.activeBalance[asset] = availableAmount * (1 / curs)
        else:
            pass


    @staticmethod
    def returnBet(curs,asset,difference):
        Bets.balance_USDT += Bets.activeBalance[asset] * curs
        Bets.activeBalance[asset] = 0
        DataBaseManager.itSelf.CapitalGainDB.insert(
            asset_name=asset,
            method="bestMultivariateRegression",
            capital_gain=difference,
        )
        print("RETURN BET ",asset,difference)


    @staticmethod
    def getBalance():
        return Bets.balance_USDT
