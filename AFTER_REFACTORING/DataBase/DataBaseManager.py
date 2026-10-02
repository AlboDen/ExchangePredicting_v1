from AFTER_REFACTORING.DataBase.CapitalDB import CapitalDB


class DataBaseManager (CapitalDB):
    def __abs__(self):
        return self