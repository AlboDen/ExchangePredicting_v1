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
    def createBet(curs,asset):
        print("CREATING BET ",asset)
        availableAmount = Bets.calculateAvailableAmountToBet()
        Bets.balance_USDT -= availableAmount
        Bets.activeBalance[asset] += availableAmount * (1/curs)

    @staticmethod
    def returnBet(curs,asset):
        Bets.balance_USDT += Bets.activeBalance[asset] * curs
        Bets.activeBalance[asset] = 0
        print("RETURN BET ",asset,Bets.getBalance())


    @staticmethod
    def getBalance():
        return Bets.balance_USDT
