import statistics
import threading
import itertools
from operator import index

from PIL.ImageChops import difference
from itertools import combinations
import math
from network.DataBase.DataBaseManager import DataBaseManager

from pybit import asset

# from Calculations.statisticsMethods import Statistic
from network.BybitExchange import BybitExchange
from Bets.Bets import Bets
import os
import time
import json
import numpy as np
from pathlib import Path

from network.DataBase.plugins.eraCapitalGainsDB import EraCapitalGainsDB
from itertools import product


class System:
    printingEraMethodsRates_FLAG = False

    itSelf = None
    settingFile = None
    lastEraCapital = 0
    assetBestMethods={}
    @staticmethod
    def forsedPutSystem():

        def stopAllMethodsThreads():
            for i in System.itSelf.assets:   # asset`s enuminator
                for m in System.itSelf.settingFile[i]:  # plugin methods of asset enuminator
                    if m != "BEST_METHOD_FROM_LAST_ITERATION":
                        params_number = len(System.itSelf.settingFile[i][m].keys())
                        for j in combinations(System.AssetSubSystem.rangeOfParametrChanging, params_number):
                            key = (m,) + tuple(j)
                            System.itSelf.assetSubSystems[i].methods[key]._stopChecker()

        print("closed All Threads")
        def getLast_best_methods():
            current_plus00percent_methods = {}
            for i in System.itSelf.assets:   # asset`s enuminator
                allImplementedMethodOfAsset_dict = System.itSelf.assetSubSystems[i].methods
                # print("allImplementedMethodOfAsset_dict",allImplementedMethodOfAsset_dict)
                for m in System.itSelf.settingFile[i]: # plugin methods of asset enuminator
                    if m != "BEST_METHOD_FROM_LAST_ITERATION":
                        params_number = len(System.itSelf.settingFile[i][m].keys())
                        key = (m,) + ("+00%",) * params_number

                        current_plus00percent_methods[i] = {}
                        current_plus00percent_methods[i][m] = allImplementedMethodOfAsset_dict[key]
            return current_plus00percent_methods
        def getLast_righted_methods():
            current_plus00percent_methods = {}
            for i in System.itSelf.assets:   # asset`s enuminator
                allImplementedMethodOfAsset_dict = System.itSelf.assetSubSystems[i].methods
                # print("allImplementedMethodOfAsset_dict",allImplementedMethodOfAsset_dict)
                for m in System.itSelf.settingFile[i]: # plugin methods of asset enuminator
                    if m != "BEST_METHOD_FROM_LAST_ITERATION":
                        params_number = len(System.itSelf.settingFile[i][m].keys())
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
            for i in System.itSelf.assets:   # asset`s enuminator
                for m in System.itSelf.settingFile[i]: # plugin methods of asset enuminator

                    try:
                        access_to_params = current_righted_methods[i][m]
                    except KeyError:
                        continue
                    try:
                        DataBaseManager.itSelf.MethodsDataDB[i].fill_results(
                            capital_gain=access_to_params.capitagGain,
                            capital_loss=access_to_params.losses,
                            error_count=-access_to_params.errorsNumber
                        )
                    except ValueError:
                        DataBaseManager.itSelf.MethodsDataDB[i].add_method(
                            #     # exchange_time, parameters, method_name
                                parameters=[],
                                method_name=""
                            )
                        DataBaseManager.itSelf.MethodsDataDB[i].fill_results(
                            capital_gain=access_to_params.capitagGain,
                            capital_loss=access_to_params.losses,
                            error_count=-access_to_params.errorsNumber
                        )
        def getBestMehodsDict(current_righted_methods = {}):
            bestMethodsDict = {}
            for i in System.itSelf.assets:   # asset`s enuminator
                print(". . . > asset ", i)
                assetBestMethods = []

                def defineMaximumCapitalGain_asset():
                    allImplementedMethodOfAsset_dict = System.itSelf.assetSubSystems[i].methods
                    # print("allImplementedMethodOfAsset_dict",allImplementedMethodOfAsset_dict)
                    maximumCapitalGain_asset = float('-inf')
                    minimumErrorsNumber_asset = float('inf')
                    minimumLosses_asset = float('inf')
                    for m in System.itSelf.settingFile[i]:
                        currentPluginMethod = m
                        position = 0  # позиция ключа в кортеже (0 — первый элемент)
                        implemendetMethods_asNamed_m = [v for k, v in allImplementedMethodOfAsset_dict.items() if
                                                        len(k) > position and k[position] == currentPluginMethod]
                        # print("implemendetMethods_asNamed_m",implemendetMethods_asNamed_m)

                        maximumCapitalGain = float('-inf')
                        minimumErrorsNumber = float('inf')
                        minimumLosses = float('inf')
                        for method in implemendetMethods_asNamed_m:
                            if method.capitagGain > maximumCapitalGain:
                                maximumCapitalGain = method.capitagGain
                            if method.errorsNumber < minimumErrorsNumber:
                                minimumErrorsNumber = method.errorsNumber
                            if abs(method.losses) < abs(minimumLosses):
                                minimumLosses = method.losses

                        if maximumCapitalGain_asset < maximumCapitalGain:
                            maximumCapitalGain_asset = maximumCapitalGain
                        if minimumErrorsNumber_asset > minimumErrorsNumber:
                            minimumErrorsNumber_asset = minimumErrorsNumber
                        if abs(minimumLosses_asset) > abs(minimumLosses):
                            minimumLosses_asset = minimumLosses
                    return maximumCapitalGain_asset,minimumErrorsNumber_asset,minimumLosses_asset
                    # print("JJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ",maximumCapitalGain)

                # maximumCapitalGain_asset = float('-inf')
                maximumCapitalGain_asset,minimumErrorsNumber_asset,minimumLosses_asset = defineMaximumCapitalGain_asset()


                for m in System.itSelf.settingFile[i]: # plugin methods of asset enuminator
                    def fill_assetBestMethods_ifMethodIsTheBest(current_righted_methods, method_name):
                        print("")
                        print(". . . > method ", m)
                        # print("OOO",System.itSelf.settingFile)
                        # while True:
                        try:
                            lastIdel = current_righted_methods[i][m]

                        except KeyError:
                            rightedMthodNameOfAsset = list(current_righted_methods[i].keys())[0]
                            lastIdel = current_righted_methods[i][rightedMthodNameOfAsset]

                        allImplementedMethodOfAsset_dict = System.itSelf.assetSubSystems[i].methods
                        # print("allImplementedMethodOfAsset_dict",allImplementedMethodOfAsset_dict)
                        currentPluginMethod = m
                        position = 0  # позиция ключа в кортеже (0 — первый элемент)
                        implemendetMethods_asNamed_m = [v for k, v in allImplementedMethodOfAsset_dict.items() if
                                                        len(k) > position and k[position] == currentPluginMethod]
                        # # print("implemendetMethods_asNamed_m",implemendetMethods_asNamed_m)
                        # methodWithMaximumCapitalGain = None
                        #
                        # #костыль, но я устал;)
                        # for _ in System.itSelf.assets:
                        #     for method in implemendetMethods_asNamed_m:
                        #         if method.capitagGain > maximumCapitalGain_asset:
                        #             methodWithMaximumCapitalGain = method
                        #             maximumCapitalGain_asset = method.capitagGain

                        MAX_RATE = 0
                        BEST_METHOD = None
                        print("maximumCapitalGain", maximumCapitalGain_asset)
                        print("minimumErrorsNumber_asset", minimumErrorsNumber_asset)
                        print("minimumLosses_asset", minimumLosses_asset)
                        for method in implemendetMethods_asNamed_m:
                            print("")
                            print(". . . > method shadow ", method)
                            print(". . . > method shadow capitagGain  ",  method.capitagGain)
                            print(". . . > method shadow errorsNumber ",  method.errorsNumber)
                            print(". . . > method shadow losses       ",  method.losses)
                            #create threashold for
                            # print("if ",method.getParams("dict"), lastIdel.getParams("dict"))
                            if method.getParams("dict") == lastIdel.getParams("dict"):
                                # print(
                                #     "_____________________________________________________________________BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
                                method.EXIT_RATE += 0.75
                            if method.getParams("dict") == System.settingFile[i][m]:
                                # print("_____________________________________________________________________BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB")
                                method.EXIT_RATE += 0.75

                            if 0 <= method.capitagGain:
                                if method.capitagGain == maximumCapitalGain_asset:   method.EXIT_RATE += 2
                                if method.errorsNumber == minimumErrorsNumber_asset: method.EXIT_RATE += 0.2
                                if method.losses == minimumLosses_asset:             method.EXIT_RATE += 0.2
                            else:
                                method.EXIT_RATE -= 1


                            print(". . . > method shadow EXIT_RATE    ", method.EXIT_RATE)
                            # BEST_METHOD = method
                            # print("CCCCCCCCCCCCCCCCCCCCCCCCCCC",method.EXIT_RATE)
                            if method.EXIT_RATE > MAX_RATE:
                                MAX_RATE = method.EXIT_RATE
                                BEST_METHOD = method
                        # print("> > > > method shadow BEST       ", BEST_METHOD)

                        if BEST_METHOD is None:
                            print("> > > > ALL METHODS IS SHIT, LET`S LOOK AT INCOME")
                            BEST_IN_WORST_CAPITAL_GAIN = float('-inf')
                            for method in implemendetMethods_asNamed_m:
                                print(". . . > method shadow ", method)
                                print(". . . > method shadow capitagGain  ", method.capitagGain)
                                if method.capitagGain > BEST_IN_WORST_CAPITAL_GAIN:
                                    BEST_IN_WORST_CAPITAL_GAIN = method.capitagGain
                                    BEST_METHOD = method
                        print("> > > > method shadow BEST           ", BEST_METHOD)
                        turple_BEST_Meth = [i,m,BEST_METHOD]
                        try:
                            System.assetBestMethods[i][m] = BEST_METHOD
                        except KeyError:
                            System.assetBestMethods[i] = {}
                            System.assetBestMethods[i][m] = BEST_METHOD

                        assetBestMethods.append(turple_BEST_Meth)



                    # print("> > > > method shadow BEST from BEST ", BEST_METHOD)
                    if m != "BEST_METHOD_FROM_LAST_ITERATION":
                        maximumCapitalGain = fill_assetBestMethods_ifMethodIsTheBest(current_righted_methods, m)
                        # if maximumCapitalGain > maximumCapitalGain_asset:
                        #     maximumCapitalGain_asset = maximumCapitalGain
                # System.assetBestMethods[i] = assetBestMethods
                # print("assetBestMethods",assetBestMethods)
                def BEST_ofTheBest(assetBestMethods, current_righted_method_type):
                    MAX_EXIT_RATE = 0
                    MAX_capitalGain = float('-inf')
                    BEST_METHOD = None

                    # to exclude equal methods by exit rates
                    ExitRates = []
                    for method_turple in assetBestMethods:
                        # print("2BEST_METHOD_FROM_LAST_ITERATION = ", method_turple)
                        if "BEST_METHOD_FROM_LAST_ITERATION" not in method_turple:
                            method = method_turple[2]

                            ExitRates.append(method.EXIT_RATE)

                            if method.EXIT_RATE > MAX_EXIT_RATE:
                                MAX_EXIT_RATE = method.EXIT_RATE
                                BEST_METHOD = method
                    if all(x == ExitRates[0] for x in ExitRates):       #if all elements are equal
                        isEqualExitRatesFlag = True
                    else:
                        isEqualExitRatesFlag = False

                    if isEqualExitRatesFlag:
                        # print("BEST_METHOD = current_righted_method", current_righted_method_type)
                        """
                            Возвращает первый объект из списка, который является экземпляром base_class
                            или наследуется от него. Если такого нет — возвращает None.
                            """
                        for obj in assetBestMethods:
                            if isinstance(obj, current_righted_method_type):
                                BEST_METHOD = obj


                    else:
                        for method_turple in assetBestMethods:
                            # if 0 <= method.capitagGain:
                            #     if method.capitagGain == maximumCapitalGain:   method.EXIT_RATE += 1
                            #     if method.capitagGain >= lastIdel.capitagGain:   method.EXIT_RATE += 1
                            #     if method.errorsNumber < lastIdel.errorsNumber: method.EXIT_RATE += 1
                            #     if method.losses < lastIdel.losses:             method.EXIT_RATE += 1
                            # else:
                            #     method.EXIT_RATE = 0
                            method = method_turple[2]
                            if method.EXIT_RATE > MAX_EXIT_RATE:
                                MAX_EXIT_RATE = method.EXIT_RATE
                                BEST_METHOD = method
                    # BEST_METHOD = 0
                    # bestMethodsDict[i] = {}
                    # bestMethodsDict[i][m] = BEST_METHOD
                    # print("BEST_METHODBEST_METHOD",BEST_METHOD)
                    return BEST_METHOD

                keyOfCurrentMethods = list(current_righted_methods[i].keys())[0]
                type_of_current_righted_method_of_asset = type(current_righted_methods[i][keyOfCurrentMethods])
                # print("type_of_current_righted_method_of_asset",type_of_current_righted_method_of_asset)
                bestMethodsDict[i] = BEST_ofTheBest(assetBestMethods,type_of_current_righted_method_of_asset)
                print(". . . > BEST_ofTheBest ",bestMethodsDict[i])
                print("")

            return bestMethodsDict
        def save_next_righted_methods_params(next_righted_methods={}):
            for i in System.itSelf.assets:  # asset`s enuminator
                # for m in System.itSelf.settingFile[i]:  # plugin methods of asset enuminator
                #     if m != "BEST_METHOD_FROM_LAST_ITERATION":
                try:
                    # print("next_righted_methods",next_righted_methods)
                    access_to_params = next_righted_methods[i]
                except KeyError:
                    # print("{{{{{{{{{{{{{{{{")
                    continue
                DataBaseManager.itSelf.MethodsDataDB[i].add_method(
                    # exchange_time, parameters, method_name
                    parameters=access_to_params.getParams(),
                    method_name=type(access_to_params).__name__
                )
        def uploadJSONMethod(bestMehodsDict):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, "systemSettings.json")
            with open(config_path, "r", encoding="utf-8") as f:
                System.settingFile = json.load(f)
                System.itSelf.assets = list(System.settingFile.keys())

            for i in System.itSelf.assets:   # asset`s enuminator
                for m in System.itSelf.settingFile[i]: # plugin methods of asset enuminator
                    print("m",m)
                    #     # for p in range(len(self.settingFile[i][m])):
                    # print("................................................", getLast_best_methods[i])
                    if m == "BEST_METHOD_FROM_LAST_ITERATION":
                        System.itSelf.settingFile[i][m] = type(bestMehodsDict[i]).__name__
                    else:
                    # print("bestMehodsDict................................................", bestMehodsDict)
                    #     if type(bestMehodsDict[i]).__name__ == m: #best of the best
                    #         System.itSelf.settingFile[i][m] = bestMehodsDict[i].getParams("dict")
                    #     else:
                    #         print("VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV",System.assetBestMethods)
                    #         # if m == System.itSelf.settingFile[i][m]:
                        waste = System.assetBestMethods[i][m].getParams("dict")
                        System.itSelf.settingFile[i][m] = waste
                        # print("VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV", waste)

            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, "systemSettings.json")
            file_path = Path(config_path)
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(System.settingFile, f, indent=2, ensure_ascii=False)
        def save_era_achivements(total_gain,currentEraCapital,current_righted_methods):

            def getEraCapitalGainOfAssets(current_righted_methods):
                dict = {}
                for i in System.itSelf.assets:  # asset`s enuminator
                    amountCapitalGainOfAssetMethod = 0
                    # print("current_righted_methods",current_righted_methods)
                    for m in System.itSelf.settingFile[i]:  # plugin methods of asset enuminator
                        try:
                            amountCapitalGainOfAssetMethod += current_righted_methods[i][m].capitagGain
                        except KeyError:
                            pass
                    dict[i] = amountCapitalGainOfAssetMethod


                return dict
            # DataBaseManager.itSelf.EraCapitalGainsDB.
            DataBaseManager.itSelf.EraCapitalGainsDB.insert(
                settings= System.settingFile,
                total_gain=total_gain,
                capital=currentEraCapital,
                asset_gains=getEraCapitalGainOfAssets(current_righted_methods = current_righted_methods),
            )


        stopAllMethodsThreads()
        time.sleep(5)
        current_righted_methods = getLast_righted_methods()
        save_current_righted_methods_params(current_righted_methods)
        bestMehodsDict = getBestMehodsDict(current_righted_methods)
        # print("HHHHHHHHHHHHHHH", System.assetBestMethods)
        save_next_righted_methods_params(bestMehodsDict)
        uploadJSONMethod(bestMehodsDict)

        currentEraCapital = Bets.getBalance()
        if System.lastEraCapital == 0:
            System.lastEraCapital = Bets.initialBalance_USDT
        eraCapitalGain = currentEraCapital - System.lastEraCapital
        print("Saldo:       ", eraCapitalGain)
        print("All capital: ", currentEraCapital)

        save_era_achivements(total_gain = eraCapitalGain, currentEraCapital = currentEraCapital, current_righted_methods=current_righted_methods)

        print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        print("")
        System.lastEraCapital = currentEraCapital


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
            def getAssetSettingsFromJSON():

                data =dict(System.settingFile[self.asset])
                key_to_exclude = "BEST_METHOD_FROM_LAST_ITERATION"
                ret = {k: v for k, v in data.items() if k != key_to_exclude}
                # print("FUNC: getAssetSettingsFromJSON",ret)
                return ret # dictionary without bestMethod pole
            self.assetSettingsFromJSON = getAssetSettingsFromJSON() # are .json loaded nimbers for modules code
            # self.assetMethodsNamesFromJSON = list(self.assetSettingsFromJSON.keys())
            # time.sleep(5)
            print("Setting of an asset ", asset)
            # print ("BEFORE System.settingFile",System.settingFile)
            # print("self.assetSettingsFromJSON ",self.assetSettingsFromJSON )
            # print("System.AssetSubSystem.predictMethodsFromPluginFiles", System.AssetSubSystem.predictMethodsFromPluginFiles)

            # research and fix differens between JSON and PLUGS
            def getPredictMethodsFromPluginFiles_withoutIGNOREDfiles():

                RELATIVE_PLUGIN_PATH = "../System/plugins"
                base_dir = os.path.dirname(os.path.abspath(__file__))
                with open(os.path.normpath(os.path.join(base_dir, RELATIVE_PLUGIN_PATH, "IGNORE")),
                          "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f]
                # the list of plugins without ignored plugs
                ret = {k: v for k, v in System.AssetSubSystem.predictMethodsFromPluginFiles.items() if k not in lines}
                # print("FUNC: getPredictMethodsFromPluginFiles_withoutIGNOREDfiles", ret)
                return ret

            self.fix_JSONandPLUGINS_differance(
                JSON = getAssetSettingsFromJSON(),                          #под все методы по конкретному активу
                PLUG=getPredictMethodsFromPluginFiles_withoutIGNOREDfiles()    # заготовки методов
            )

            # while True:pass
            self.methods = {}
            for name, mod in System.AssetSubSystem.predictMethodsFromPluginFiles.items():
                # one-demention array of JSON params
                params = list(self.assetSettingsFromJSON[name].values())
                # print("params",params)
                # N-demention array with deviation of JSON params in rangeOfParametrChanging list
                spectr = self.createParametrSpector(params=params,ranges_percent=System.AssetSubSystem.rangeOfParametrChanging)
                # print("spectr", spectr)

                # Проверяем, есть ли в модуле класс c именем файла (чтобы не упасть с ошибкой, если класса нет)
                if hasattr(mod, name):
                    # Получаем сам класс метода из модуля по имени — теперь Cls это «чертёж» класса, а не экземпляр
                    Cls = getattr(mod, name)
                    # for num_of_param in range(len(params)):
                    for keys in itertools.product(self.rangeOfParametrChanging, repeat=len(params)):
                        # print("1keys", keys)
                        rightToMakeBet = False
                        condition = True
                        for var in keys:
                            buf_arr = np.array(var)
                            char1 = np.char.slice(buf_arr, 1, 2)  # 2‑й символ (индекс 1)
                            char2 = np.char.slice(buf_arr, 2, 3)  # 3‑й символ (индекс 2)
                            condition = condition and (char1 == "0") and (char2 == "0")

                        BEST_METHOD_FROM_LAST_ITERATION = System.settingFile[self.asset]["BEST_METHOD_FROM_LAST_ITERATION"]
                        currant_name_of_the_method_parant = name
                        condition_2 = BEST_METHOD_FROM_LAST_ITERATION == currant_name_of_the_method_parant

                        # bestOftheBest_settings = System.settingFile[self.asset]["BEST_METHOD_FROM_LAST_ITERATION"]
                        # print("bestOftheBest_settings",bestOftheBest_settings)
                        # print("System.settingFile[self.asset]",System.settingFile[self.asset])
                        if condition and condition_2: # and (System.settingFile[self.asset] == bestOftheBest_settings):
                            print("\tGIVED BET RULES for ", self.asset, Cls)
                            rightToMakeBet = True

                        param_vector = self.get_by_keys(spectr, keys)[0]
                        # print("param_vector", param_vector)
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
                # print("JSON", list(JSON.keys()))
                # print("System.AssetSubSystem.predictMethodsFromPluginFiles", list(System.AssetSubSystem.predictMethodsFromPluginFiles.keys()))
                if len(JSON.keys()) < len(PLUG.keys()): # if was added new plugin
                    print("WAS ADDED NEW PLUGS, LOADING PARAMS")
                    # print("WAS ADDED NEW PLUGS, LOADING PARAMS",PLUG)
                    for key in PLUG.keys():
                        # print("key", key,System.AssetSubSystem.predictMethodsFromPluginFiles[key])
                        if key not in JSON.keys():
                            RELATIVE_PLUGIN_PATH = "../System/plugins"
                            base_dir = os.path.dirname(os.path.abspath(__file__))

                            module = PLUG[key]
                            with open(os.path.normpath(os.path.join(base_dir, RELATIVE_PLUGIN_PATH, "IGNORE")),
                                      "r", encoding="utf-8") as f:
                                lines = [line.strip() for line in f]
                            if module not in lines:
                                cls_name = module.__name__
                                index_ofLast_point = cls_name.rfind(".")
                                if index_ofLast_point != -1:
                                    cls_name = cls_name[index_ofLast_point + 1:]
                                cls = getattr(module, cls_name)
                                print("WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW")
                                System.settingFile[self.asset][key] = cls.loadBasicParams(self.asset)
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    config_path = os.path.join(script_dir, "systemSettings.json")
                    file_path = Path(config_path)

                    with file_path.open("w", encoding="utf-8") as f:
                        json.dump(System.settingFile, f, indent=2, ensure_ascii=False)

                    with open(config_path, "r", encoding="utf-8") as f:
                        reading = json.load(f)[self.asset]
                        self.assetSettingsFromJSON  = reading
                        JSON = reading

                    #clearJSON for BEST_METHOD_FROM_LAST_ITERATION
                    data = JSON
                    key_to_exclude = "BEST_METHOD_FROM_LAST_ITERATION"
                    JSON = {k: v for k, v in data.items() if k != key_to_exclude}
                    # return
                    # print("PLUG ",PLUG)
                    # print("JSON ", JSON)
                # if was deleted plugin
                if len(JSON.keys()) > len(PLUG.keys()):  # if was deleted plugin
                    print("WAS DELETED PLUGS, del PARAMS")
                    # print("JSON.keys()",JSON.keys())
                    # print("System.AssetSubSystem.predictMethodsFromPluginFiles.keys()",System.AssetSubSystem.predictMethodsFromPluginFiles.keys())
                    for key in JSON.keys():
                        # print("key", key)
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
                    # return
                # if was changed plugin
                if not set(list(JSON)).issubset(set(list(PLUG))): #if elems of JSON array are included into PLUG array
                # if not list(JSON.keys()) not in list(PLUG.keys()):
                    print("if was changed plugin",JSON.keys(),PLUG.keys(),set(list(JSON)).issubset(set(list(PLUG))))
                    # print("System.settingFile FIXING changings", System.settingFile)
                    for key in list(PLUG.keys()):
                        # print("keys", key)
                        if key not in JSON.keys():
                            # print("key", key)
                            System.settingFile[self.asset][key] = None
                    # print("System.settingFile",System.settingFile)
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    config_path = os.path.join(script_dir, "systemSettings.json")
                    file_path = Path(config_path)
                    print("System.settingFile BEFORE WRITING ",System.settingFile)
                    with file_path.open("w", encoding="utf-8") as f:
                        json.dump(System.settingFile, f, indent=2, ensure_ascii=False)
                    with open(config_path, "r", encoding="utf-8") as f:
                        file = json.load(f)
                        reading = file[self.asset]
                        print("System.settingFile AFTER WRITING ", reading)
                        self.assetSettingsFromJSON = reading
                        System.settingFile = file
                    self.assetSettingsFromJSON = dict(System.settingFile[self.asset])
                    print("AFFFFFFFFFFFFFFFFF ", System.settingFile)
                    return
                    try:
                        for key in JSON.keys():
                            RELATIVE_PLUGIN_PATH = "../System/plugins"
                            base_dir = os.path.dirname(os.path.abspath(__file__))
                            # print("System.AssetSubSystem.predictMethodsFromPluginFiles", System.AssetSubSystem.predictMethodsFromPluginFiles)
                            module = System.AssetSubSystem.predictMethodsFromPluginFiles[key]
                            with open(os.path.normpath(os.path.join(base_dir, RELATIVE_PLUGIN_PATH, "IGNORE")),
                                      "r", encoding="utf-8") as f:
                                lines = [line.strip() for line in f]
                                # print("IGNORING PLUGINS SPECIFICATION", lines)
                            if module not in lines:
                                # print("module",module)
                                cls_name = module.__name__
                                index_ofLast_point = cls_name.rfind(".")
                                if index_ofLast_point != -1:
                                    cls_name = cls_name[index_ofLast_point+1:]
                                # print("cls_name ",cls_name)
                                cls = getattr(module, cls_name)
                            # print("cls ",cls)

                            if JSON[key] == None:
                                JSON[key] = {}
                            if JSON[key].keys() != cls.loadBasicParams().keys()\
                                    and list(JSON[key].keys()) not in list(cls.loadBasicParams().keys()):
                                # print("DDDDDDDDDDDDDDDDDDDDDDDD", JSON[key].keys())
                                # print("DDDDDDDDDDDDDDDDDDDDDDDD", System.AssetSubSystem.predictMethodsFromPluginFiles[key].integralLaggedSubsystem.loadBasicParams(self).keys())
                                print("DDDDDDDDDDDDDDDDDDDDDDDD", System.AssetSubSystem.predictMethodsFromPluginFiles)
                                print("WAS CHANGET PARAMETRS SPECIFICATION")
                                script_dir = os.path.dirname(os.path.abspath(__file__))
                                config_path = os.path.join(script_dir, "systemSettings.json")
                                file_path = Path(config_path)
                                System.settingFile[self.asset][key] = cls.loadBasicParams(self.asset)

                                # self.assetSettingsFromJSON[key]
                                with file_path.open("w", encoding="utf-8") as f:
                                    json.dump(System.settingFile, f, indent=2, ensure_ascii=False)

                                with open(config_path, "r", encoding="utf-8") as f:
                                    reading = json.load(f)[self.asset]
                                    self.assetSettingsFromJSON = reading
                                    JSON = reading
                    except KeyError:
                        print("WAS CHANGED LIST PLUGINS")

        def createParametrSpector(self, params, ranges_percent):
            """
                Генерирует словарь сценариев отклонений параметров.

                Параметры:
                - params: список числовых параметров (например, [100, 200, 50])
                - ranges_percent: список строк с процентами (например, ["-20%", "+00%", "+20%"])

                Возвращает:
                Словарь вида:
                {
                  ("+20%", "-20%", "+00%"): [120.0, 160.0, 50.0],  # ключ - кортеж процентов, значение - изменённые параметры
                  ("-20%", "+00%", "+20%"): [80.0, 200.0, 60.0],
                  ...
                }

                Логика:
                Для каждой комбинации процентов из ranges_percent создается ключ (кортеж).
                Соответствующее значение — это список, где каждый исходный параметр изменен на процент из позиции ключа.
                """
            n = len(params)
            result = {}

            # Генерируем все возможные комбинации процентов длиной n (декартово произведение)
            combinations = product(ranges_percent, repeat=n)

            for combo in combinations:
                # combo - это кортеж, например ("+20%", "-20%", "+00%")

                modified_params = []
                for i, percent_str in enumerate(combo):
                    base_val = params[i]

                    # Парсим строку процента: убираем '%', преобразуем в float
                    try:
                        percent_val = float(percent_str.replace('%', ''))
                    except ValueError:
                        raise ValueError(
                            f"Некорректный формат процента: {percent_str}. Ожидается формат вида '+20%', '-5%' или '0%'.")

                    # Вычисляем новое значение: base + (base * percent/100)
                    new_val = base_val * (1 + percent_val / 100.0)
                    modified_params.append(new_val)

                # Используем combo как ключ (он уже кортеж), modified_params как значение
                result[combo] = modified_params

            return result

        def get_by_keys(self, grid, keys):
            """Обращение по строкам-ключам: ('-25%', '0%', '+25%') -> одномерный массив."""
            # print("grid[keys] " , grid[keys])
            return [grid[keys]]
