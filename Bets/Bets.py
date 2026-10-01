class Bets:
    balance_USDT = 0

    activeBalance_BTC = 0

    @staticmethod
    def toUpBalance_USDT(payment):
        Bets.balance_USDT += payment


    @staticmethod
    def calculateAvailableAmountToBet():
        if Bets.balance_USDT > 5000:
            return Bets.balance_USDT*0.1
        return 0

    @staticmethod
    def createBet(curs):
        print("CREATING BET",Bets.balance_USDT)
        availableAmount = Bets.calculateAvailableAmountToBet()
        Bets.balance_USDT -= availableAmount
        Bets.activeBalance_BTC += availableAmount * (1/curs)

    @staticmethod
    def returnBet(curs):
        print("RETURN BET",Bets.balance_USDT)
        Bets.balance_USDT += Bets.activeBalance_BTC * curs
        Bets.activeBalance_BTC = 0

    @staticmethod
    def getBalance():
        return Bets.balance_USDT
