from network.DataBase import DataBaseManager
from network.DataBase.DataBaseManager import DataBaseManager
from network.BybitExchange import BybitExchange

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
        return 1000
        if Bets.balance_USDT > 5000:
            return Bets.balance_USDT*0.1
        return 0

    @staticmethod
    def createBet(asset,rightToMakeBet = False):
        if rightToMakeBet:
            # print("HHHHH ",Bets.balance_USDT)
            print("CREATING BET ",asset)
            # setted_order = BybitExchange.session_trade.place_order(
            #     category="spot",
            #     symbol="XRPUSDT",
            #     side="Buy",vb
            #     orderType="Market",
            #     qty=7
            # )
        else:
            # print("CREATING SHADOW BET ", asset)
            pass

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
            # XRP_balanse = BybitExchange.session_trade.get_coin_balance(
            #     accountType="UNIFIED",
            #     coin="XRP"
            # )
            #
            # XRP_money = XRP_balanse['result']['balance']['walletBalance']
            # print(XRP_money)
            #
            # setted_order = BybitExchange.session_trade.place_order(
            #     category="spot",
            #     symbol="XRPUSDT",
            #     side="Sell",
            #     orderType="Market",
            #     qty=round(float(XRP_money), 2)
            # )
            # print("HHHHH ", Bets.balance_USDT, incrementToBalance_USDT)
            DataBaseManager.itSelf.CapitalGainDB.insert(
                asset_name=asset,
                method=method,
                capital_gain=capitagGain,
            )
            Bets.balance_USDT += incrementToBalance_USDT
            # print("RETURN BET IDEAL ", asset, capitagGain)
            print("RETURN BET REAL ", asset, capitagGain)
            # print("HHHHH ", Bets.balance_USDT, incrementToBalance_USDT)
        else:
            # print("RETURN SHADOW BET ", asset, capitagGain)
            pass
        return 0


    @staticmethod
    def getBalance():
        return Bets.balance_USDT
