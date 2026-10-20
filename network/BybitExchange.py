import random
import os
import threading
import numpy as np
from pybit.unified_trading import HTTP
from requests import session

from network.DataBase.plugins.capitalGainDB import CapitalGainDB
# from Calculations.statisticsMethods import Statistic
from network.plugins.BybitSpotLimiter import BybitSpotLimiter

import time
class BybitExchange (BybitSpotLimiter):
    demoMode = True
    testnet = False
    # norm test
    api_key = "ZotNYzW49ASjZuIM6f"
    api_secret = "YWVdQ7iYhnZmIn7lzx1wq3QdVy8FzA8CX5E0"
    #active
    # api_key = "la2CNjdpR7fHsBgCXL"
    # api_secret = "pntv7WLZK7XrD3wmlCfD6ps6CrAhPyIXR6Df"


    session = HTTP(
        testnet = testnet,
        demo = demoMode,
        api_key=api_key,
        api_secret=api_secret,
    )

    class Klines:
        @staticmethod
        def getIndexPrices(symbol: str, hours_back: int = 5, interval: int = 1) -> np.ndarray:
            """
               Запрашивает у Bybit свечи маркировочной цены (эндпоинт /v5/market/mark-price-kline)
               начиная с hours_back часов назад до текущего момента с шагом interval минут.

               :param symbol: Имя валютной пары (например, 'BTCUSDT', 'ETHUSDT').
               :param hours_back: Сколько часов назад начинается запрос.
               :param interval: Интервал свечи в минутах: '1', '3', '5', '15', '30', '60',
                                '120', '240', '360', '720', 'D', 'W', 'M'.
               :return: np.array с ценами закрытия в хронологическом порядке (от старых к новым).
                        Пустой массив, если данных нет или произошла ошибка.
               """
            if not symbol:
                raise ValueError("symbol не может быть пустым")
            if hours_back <= 0:
                raise ValueError("hours_back должен быть положительным числом")

            end_time = int(time.time() * 1000)
            start_time = end_time - hours_back * 60 * 60 * 1000  # часы -> миллисекунды

            # Для публичного эндпоинта ключи не нужны
            session = HTTP()

            tringCycle_FLAG = True
            while tringCycle_FLAG:

                try:
                    resp = session.get_index_price_kline(
                        category="linear",  # mark-price-kline доступен только для деривативов
                        symbol=symbol,
                        interval=str(interval),
                        start=start_time,
                        end=end_time,
                        limit = hours_back*hours_back/interval/60
                    )
                    tringCycle_FLAG = False
                except Exception as e:
                    print(f"Ошибка запроса к Bybit в getIndexPrices: {e}",symbol)
                    min_val = 1
                    max_val = 2
                    rand = min_val + random.random() * (max_val - min_val)
                    time.sleep(round(rand))
                    # return np.array([], dtype=float)

            if resp.get("retCode") != 0:
                print(f"Bybit вернул ошибку: retCode={resp.get('retCode')}, msg={resp.get('retMsg')}")
                return np.array([], dtype=float)

            data = resp.get("result", {}).get("list", [])
            if not data:
                return np.array([], dtype=float)

            # Каждая свеча — список: [startTime, open, high, low, close]
            prices = []
            for k in data:
                if not isinstance(k, (list, tuple)) or len(k) < 5:
                    continue
                try:
                    prices.append(float(k[4]))  # close — индекс 4
                except (ValueError, TypeError):
                    continue

            # Bybit отдаёт свечи от новых к старым — разворачиваем в хронологический порядок
            return np.array(prices[::-1], dtype=float)

        @staticmethod
        def get_current_price(symbol: str) -> float | None:
            resp = BybitExchange.session.get_tickers(
                    category="linear",  # mark-price-kline доступен только для деривативов
                    symbol=symbol,
                )
            time.sleep(0.2)
            return float(resp["result"]["list"][0]["indexPrice"])

