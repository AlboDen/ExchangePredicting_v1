import statistics
import threading
import itertools
from PIL.ImageChops import difference
from itertools import combinations
import math
from Calculations.statisticsMethods import Statistic
from network.BybitExchange import BybitExchange
from Bets.Bets import Bets
import os
import time
import json
import numpy as np

class System:
    itSelf = None
    settingFile = None


    def __init__(self):  #creates several AssetSubsystems according to number of assets
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "./systemSettings.json")
        with open(config_path, "r", encoding="utf-8") as f:
            System.settingFile = json.load(f)
            self.assets = list(System.settingFile.keys())

        self.assetSubSystems = {}
        for i in self.assets:
            self.assetSubSystems[i] = System.AssetSubSystem(i)

    # we are already know name of asset
    # class creates several plugged methods for selected asset
    # and 10*n shadow methods ("n" is a number of specific method parametrs)
    class AssetSubSystem:
        predictMethodsFromPluginFiles = {} # are ".py" loaded modules code (by shadowProcess)
        rangeOfParametrChanging = ["-20%", "+00%", "+20%"]


        def __init__(self, asset):

            self.asset = asset
            self.assetSettingsFromJSON = dict(System.settingFile[self.asset]) # are .json loaded nimbers for modules code
            self.assetMethodsNamesFromJSON = list(self.assetSettingsFromJSON.keys())
            print("asset", asset)

            # research the case when from JSON getted less methodsSettings then exist plugins
            if len(self.assetMethodsNamesFromJSON) < len(System.AssetSubSystem.predictMethodsFromPluginFiles.keys()):
                pass

            # research the case when from JSON getted more methodsSettings then exist plugins
            if len(self.assetMethodsNamesFromJSON) < len(System.AssetSubSystem.predictMethodsFromPluginFiles.keys()):
                pass

            self.methods = {}

            for name, mod in System.AssetSubSystem.predictMethodsFromPluginFiles.items():
                # one-demention array of JSON params
                params = list(self.assetSettingsFromJSON[name].values())
                # N-demention array with deviation of JSON params in rangeOfParametrChanging list
                spectr = self.createParametrSpector(params)
                print("spectr", spectr)

                # Проверяем, есть ли в модуле класс c именем файла (чтобы не упасть с ошибкой, если класса нет)
                if hasattr(mod, name):
                    # Получаем сам класс метода из модуля по имени — теперь Cls это «чертёж» класса, а не экземпляр
                    Cls = getattr(mod, name)
                    for num_of_param in range(len(params)):
                        for keys in itertools.product(self.rangeOfParametrChanging, repeat=len(params)):
                            # print("keys", (num_of_param,)+keys)
                            param_vector = self.get_by_keys(spectr, keys)
                            # Создаём экземпляр класса
                            instance = Cls(self.asset, param_vector)

                            self.methods[ tuple([name]+ list(keys)) ] = instance



        def createParametrSpector(self, params=None):
            """
            Принимает одномерный массив параметров.

            Возвращает n-мерный массив shape (k, k, ..., k, n),
            где k — длина диапазона отклонений (например, 11 при шаге 5% от -25% до +25%),
            а n — количество параметров:
                - по индексам первых n осей — отклонение соответствующего параметра;
                - на последней оси (длины n) — сами значения параметров
                  с учётом всех накопленных отклонений.
            """
            grid = {}
            # print("params",params)
            for variable in range(len(params)):
                n = len(self.rangeOfParametrChanging)
                # gragationMatrix = np.zeros((n, n), dtype=float)
                medium = math.ceil(n / 2)
                for i, a in enumerate(self.rangeOfParametrChanging):
                    for j, b in enumerate(self.rangeOfParametrChanging):
                        if i == medium:
                            persent = float(b[0:3]) / 100
                            # print("persent", persent)
                            if persent != 0:
                                # print("<>0")
                                persent = persent + 1
                            else:
                                # print("=0")
                                persent = 1

                            grid[(variable, b)] = params[variable]*persent

            end_grid = {}
            # костыль
            for a,b in combinations(range(len(params)),2):
                for i in self.rangeOfParametrChanging:
                    for j in self.rangeOfParametrChanging:
                        end_grid[(i,j)] = [grid[(a, i)], grid[(b, j)]]
                        # print("JJJ ", [grid[(variable, i)], grid[(variable, j)]])
                    # end_grid[(variable, i, j)] =

            return end_grid

        def get_by_keys(self, grid, keys):
            """Обращение по строкам-ключам: ('-25%', '0%', '+25%') -> одномерный массив."""
            return grid[keys]
