from network.DataBase.plugins.capitalGainDB import CapitalGainDB
from network.DataBase.plugins.methodDataDB import MethodDataDB
from network.DataBase.plugins.eraCapitalGainsDB import EraCapitalGainsDB



class DataBaseManager():
    itSelf = None
    def __init__(self,assets = {}):
        self.CapitalGainDB = CapitalGainDB()
        self.EraCapitalGainsDB = EraCapitalGainsDB()
        self.MethodsDataDB = {f"{i}":MethodDataDB(i) for i in assets}
        pass
