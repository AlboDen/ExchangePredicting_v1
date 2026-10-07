import statistics
import threading
import itertools
from PIL.ImageChops import difference
from itertools import combinations
import math
from network.DataBase.DataBaseManager import DataBaseManager

from pybit import asset

from Calculations.statisticsMethods import Statistic
from network.BybitExchange import BybitExchange
from Bets.Bets import Bets
import os
import time
import json
import numpy as np
from pathlib import Path

class System:
    itSelf = None
    settingFile = None

    def closeAllThreads(self):
        print("closeAllThreads")
        def stopAllMethodsThreads():
            for i in self.assets:   # asset`s enuminator
                for m in self.settingFile[i]:  # plugin methods of asset enuminator
                    params_number = len(self.settingFile[i][m].keys())
                    for j in combinations(System.AssetSubSystem.rangeOfParametrChanging, params_number):
                        key = (m,) + tuple(j)
                        System.itSelf.assetSubSystems[i].methods[key]._stopChecker()

        def getLast_righted_methods():
            current_plus00percent_methods = {}
            for i in self.assets:   # asset`s enuminator
                allImplementedMethodOfAsset_dict = System.itSelf.assetSubSystems[i].methods
                # print("allImplementedMethodOfAsset_dict",allImplementedMethodOfAsset_dict)
                for m in self.settingFile[i]: # plugin methods of asset enuminator
                    params_number = len(self.settingFile[i][m].keys())
                    key = (m,) + ("+00%",) * params_number
                    if allImplementedMethodOfAsset_dict[key].rightToMakeBet:
                        current_plus00percent_methods[i] = {}
                        try:
                            current_plus00percent_methods[i][m] = allImplementedMethodOfAsset_dict[key]
                        except KeyError:
                            current_plus00percent_methods[i] = {}
                            current_plus00percent_methods[i][m] = allImplementedMethodOfAsset_dict[key]
            return current_plus00percent_methods
        def save_current_righted_methods_params(current_righted_methods = {}):
            for i in self.assets:   # asset`s enuminator
                for m in self.settingFile[i]: # plugin methods of asset enuminator

                    try:
                        access_to_params = current_righted_methods[i][m]
                    except KeyError:
                        continue

                    DataBaseManager.itSelf.MethodsDataDB[i].fill_results(
                        capital_gain=access_to_params.capitagGain,
                        capital_loss=access_to_params.losses,
                        error_count=-access_to_params.errorsNumber
                    )
        def getBestMehodsDict(current_righted_methods = {}):


            bestMethodsDict = {}
            for i in self.assets:   # asset`s enuminator
                for m in self.settingFile[i]: # plugin methods of asset enuminator
                    try:
                        lastIdel = current_righted_methods[i][m]
                    except KeyError:
                        continue

                    allImplementedMethodOfAsset_dict = System.itSelf.assetSubSystems[i].methods

                    currentPluginMethod = m
                    position = 0  # позиция ключа в кортеже (0 — первый элемент)
                    implemendetMethods_asNamed_m = [v for k, v in allImplementedMethodOfAsset_dict.items() if
                                         len(k) > position and k[position] == currentPluginMethod]
                    MAX_RATE = 0
                    BEST_METHOD = None
                    for method in implemendetMethods_asNamed_m:
                        if 0 < method.capitagGain:
                            if method.capitagGain > lastIdel.capitagGain:   method.EXIT_RATE += 1
                            if method.errorsNumber < lastIdel.errorsNumber: method.EXIT_RATE += 1
                            if method.losses < lastIdel.losses:             method.EXIT_RATE += 1
                        else:
                            method.EXIT_RATE = 0
                        BEST_METHOD = method
                        # print("CCCCCCCCCCCCCCCCCCCCCCCCCCC",method.EXIT_RATE)
                        if method.EXIT_RATE > MAX_RATE:
                            MAX_RATE = method.EXIT_RATE
                            BEST_METHOD = method
                    try:
                        bestMethodsDict[i][m] = BEST_METHOD
                    except KeyError:
                        bestMethodsDict[i] = {}
                        bestMethodsDict[i][m] = BEST_METHOD

            return bestMethodsDict
        def save_next_righted_methods_params(next_righted_methods={}):
            for i in self.assets:  # asset`s enuminator
                for m in self.settingFile[i]:  # plugin methods of asset enuminator
                    try:
                        access_to_params = next_righted_methods[i][m]
                    except KeyError:
                        print("{{{{{{{{{{{{{{{{")
                        continue
                    DataBaseManager.itSelf.MethodsDataDB[i].add_method(
                        # exchange_time, parameters, method_name
                        parameters=access_to_params.getParams(),
                        method_name=m
                    )

        current_righted_methods = getLast_righted_methods()
        save_current_righted_methods_params(current_righted_methods)
        bestMehodsDict = getBestMehodsDict(current_righted_methods)
        save_next_righted_methods_params(bestMehodsDict)
        stopAllMethodsThreads()


    def __init__(self):  #creates several AssetSubsystems according to number of assets
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "systemSettings.json")
        with open(config_path, "r", encoding="utf-8") as f:
            System.settingFile = json.load(f)
            self.assets = list(System.settingFile.keys())
        self.assetSubSystems = {}
        for i in self.assets:
            # print("self.asset !!!!!!!!!!!!!!!!!!!!!!!!")
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
            # self.assetMethodsNamesFromJSON = list(self.assetSettingsFromJSON.keys())
            print("Setting of an asset ", asset)
            # print("self.assetSettingsFromJSON ",self.assetSettingsFromJSON )
            # print("System.AssetSubSystem.predictMethodsFromPluginFiles", System.AssetSubSystem.predictMethodsFromPluginFiles)

            # research and fix differens between JSON and PLUGS

            self.fix_JSONandPLUGINS_differance(
                JSON = self.assetSettingsFromJSON,                          #под все методы по конкретному активу
                PLUG=System.AssetSubSystem.predictMethodsFromPluginFiles    # заготовки методов
            )

            self.methods = {}
            for name, mod in System.AssetSubSystem.predictMethodsFromPluginFiles.items():
                # one-demention array of JSON params
                params = list(self.assetSettingsFromJSON[name].values())
                # N-demention array with deviation of JSON params in rangeOfParametrChanging list
                spectr = self.createParametrSpector(params)
                # print("spectr", spectr)

                # Проверяем, есть ли в модуле класс c именем файла (чтобы не упасть с ошибкой, если класса нет)
                if hasattr(mod, name):
                    # Получаем сам класс метода из модуля по имени — теперь Cls это «чертёж» класса, а не экземпляр
                    Cls = getattr(mod, name)
                    for num_of_param in range(len(params)):
                        for keys in itertools.product(self.rangeOfParametrChanging, repeat=len(params)):
                            # print("keys", keys)
                            rightToMakeBet = False

                            buf_arr = np.array(keys)
                            char1 = np.char.slice(buf_arr, 1, 2)  # 2‑й символ (индекс 1)
                            char2 = np.char.slice(buf_arr, 2, 3)  # 3‑й символ (индекс 2)
                            condition = (char1 == "0") & (char2 == "0")
                            if (char1 == "0") and (char2 == "0"):
                                print("\tGIVED BET RULES for ", self.asset)
                                rightToMakeBet = True

                            param_vector = self.get_by_keys(spectr, keys)
                            # Создаём экземпляр класса
                            instance = Cls(self.asset, param_vector, rightToMakeBet)
                            # print("instance", instance)
                            # print("tuple([name]+ list(keys))", tuple([name]+ list(keys)))
                            self.methods[ tuple([name]+ list(keys)) ] = instance
            # print("self.methods = {}",self.methods)
        def fix_JSONandPLUGINS_differance(self, JSON = {}, PLUG = {}):
            # must be ready to research several methods !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            # JSON = self.assetSettingsFromJSON,  # под все методы по конкретному активу
            # PLUG = System.AssetSubSystem.predictMethodsFromPluginFiles  # заготовки методов

            # research the case when from JSON getted less methodsSettings then exist plugins
            for _ in range(4):
                # print("WAS ADDED NEW PLUGS?", self.asset)
                # if was added new plugin
                if len(JSON.keys()) < len(System.AssetSubSystem.predictMethodsFromPluginFiles.keys()): # if was added new plugin
                    print("WAS ADDED NEW PLUGS, LOADING PARAMS")
                    # print("WAS ADDED NEW PLUGS, LOADING PARAMS",System.AssetSubSystem.predictMethodsFromPluginFiles[key])
                    for key in System.AssetSubSystem.predictMethodsFromPluginFiles.keys():
                        print("key", key,System.AssetSubSystem.predictMethodsFromPluginFiles[key])
                        if key not in JSON.keys():
                            System.settingFile[self.asset][key] = System.AssetSubSystem.predictMethodsFromPluginFiles[key].integralLaggedSubsystem.loadBasicParams(self)
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    config_path = os.path.join(script_dir, "systemSettings.json")
                    file_path = Path(config_path)

                    with file_path.open("w", encoding="utf-8") as f:
                        json.dump(System.settingFile, f, indent=2, ensure_ascii=False)

                    with open(config_path, "r", encoding="utf-8") as f:
                        reading = json.load(f)[self.asset]
                        self.assetSettingsFromJSON  = reading
                        JSON = reading

                # if was deleted plugin
                if len(JSON.keys()) > len(System.AssetSubSystem.predictMethodsFromPluginFiles.keys()):  # if was deleted plugin
                    # print("WAS DELETED PLUGS, del PARAMS")
                    for key in JSON.keys():
                        # print("key", key,System.AssetSubSystem.predictMethodsFromPluginFiles[key])
                        if key not in System.AssetSubSystem.predictMethodsFromPluginFiles.keys():
                            System.settingFile[self.asset].pop(key,None)
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    config_path = os.path.join(script_dir, "systemSettings.json")
                    file_path = Path(config_path)

                    with file_path.open("w", encoding="utf-8") as f:
                        json.dump(System.settingFile, f, indent=2, ensure_ascii=False)
                    with open(config_path, "r", encoding="utf-8") as f:
                        reading = json.load(f)[self.asset]
                        self.assetSettingsFromJSON = reading
                        JSON = reading

                for key in JSON.keys():
                    if JSON[key].keys() != System.AssetSubSystem.predictMethodsFromPluginFiles[key].integralLaggedSubsystem.loadBasicParams(self).keys()\
                            and list(JSON[key].keys()) not in list(System.AssetSubSystem.predictMethodsFromPluginFiles[key].integralLaggedSubsystem.loadBasicParams(self).keys()):
                        # print("DDDDDDDDDDDDDDDDDDDDDDDD", JSON[key].keys())
                        # print("DDDDDDDDDDDDDDDDDDDDDDDD", System.AssetSubSystem.predictMethodsFromPluginFiles[key].integralLaggedSubsystem.loadBasicParams(self).keys())
                        print("WAS CHANGET PARAMETRS SPECIFICATION")
                        script_dir = os.path.dirname(os.path.abspath(__file__))
                        config_path = os.path.join(script_dir, "systemSettings.json")
                        file_path = Path(config_path)
                        System.settingFile[self.asset][key] = System.AssetSubSystem.predictMethodsFromPluginFiles[
                            key].integralLaggedSubsystem.loadBasicParams(self)

                        # self.assetSettingsFromJSON[key]
                        with file_path.open("w", encoding="utf-8") as f:
                            json.dump(System.settingFile, f, indent=2, ensure_ascii=False)

                        with open(config_path, "r", encoding="utf-8") as f:
                            reading = json.load(f)[self.asset]
                            self.assetSettingsFromJSON = reading
                            JSON = reading


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
            # print("grid",grid)
            end_grid = {}
            # костыль
            if len(params) > 1:
                for a,b in combinations(range(len(params)),2):
                    for i in self.rangeOfParametrChanging:
                        for j in self.rangeOfParametrChanging:
                            end_grid[(i,j)] = [grid[(a, i)], grid[(b, j)]]
                            # print("JJJ ", [grid[(variable, i)], grid[(variable, j)]])
                        # end_grid[(variable, i, j)] =
            else:
                for j, b in enumerate(self.rangeOfParametrChanging):
                    end_grid[(b,)] = grid[(0,b)]
            # print("end_grid", end_grid)
            return end_grid

        def get_by_keys(self, grid, keys):
            """Обращение по строкам-ключам: ('-25%', '0%', '+25%') -> одномерный массив."""
            # print("grid[keys] " , grid[keys])
            return [grid[keys]]
