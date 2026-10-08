from network.DataBase import DataBaseManager
from network.DataBase.DataBaseManager import DataBaseManager


class Bets:
    initialBalance_USDT = 0
    balance_USDT = 0

    AvailableAmountToBetWasMadeForAsset = {}

    @staticmethod
    def toUpBalance_USDT(payment):
        Bets.balance_USDT += payment
        Bets.initialBalance_USDT  += payment

    @staticmethod
    def calculateAvailableAmountToBet():
        if Bets.balance_USDT > 5000:
            return Bets.balance_USDT*0.1
        return 0

    @staticmethod
    def createBet(asset,rightToMakeBet = False):
        if rightToMakeBet:
            # print("HHHHH ",Bets.balance_USDT)
            print("CREATING BET ",asset)
        try:
            #if exist comlitely filled available amoutn for asset Bets.AvailableAmountToBetWasMadeForAsset[asset]
            if Bets.AvailableAmountToBetWasMadeForAsset[asset] is not None:
                availableAmount_USDT = Bets.AvailableAmountToBetWasMadeForAsset[asset]
            else:
                availableAmount_USDT = Bets.calculateAvailableAmountToBet()
                Bets.AvailableAmountToBetWasMadeForAsset[asset] = availableAmount_USDT

        except KeyError:
            availableAmount_USDT = Bets.calculateAvailableAmountToBet()
            Bets.AvailableAmountToBetWasMadeForAsset[asset] = availableAmount_USDT

        if rightToMakeBet:
            Bets.balance_USDT -= availableAmount_USDT

        # activeBalance_notUSDT = availableAmount_USDT * (1/curs)
        # if rightToMakeBet:
            # print("HHHHH ", Bets.balance_USDT ,availableAmount_USDT)
        return availableAmount_USDT



    @staticmethod
    def returnBet(incrementToBalance_USDT, capitagGain, asset, method, rightToMakeBet):
        if rightToMakeBet:
            # print("HHHHH ", Bets.balance_USDT, incrementToBalance_USDT)
            DataBaseManager.itSelf.CapitalGainDB.insert(
                asset_name=asset,
                method=method,
                capital_gain=capitagGain,
            )
            Bets.balance_USDT += incrementToBalance_USDT
            print("RETURN BET ", asset, capitagGain)
            # print("HHHHH ", Bets.balance_USDT, incrementToBalance_USDT)
        return 0


    @staticmethod
    def getBalance():
        return Bets.balance_USDT
