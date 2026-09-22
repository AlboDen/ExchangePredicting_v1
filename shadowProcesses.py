import asyncio
import threading

import schedule

from network.BybitExchange import BybitExchange
from visual.graph import Graph
from visual.window import Window


class shadowProcesses:
    class RepeatedServerRequest:
        INTERVAL_BETWEEN_REPEATED_REQUEST = 10
        INTERVAL_BETWEEN_UPDATE_TIMER_LABEL = 0.1
        numberofRequest = 1

        counter = 0
        @staticmethod
        def serverRequest():
            text_info_timer = f"Время до следующего запроса данных: {str(shadowProcesses.RepeatedServerRequest.counter)} / {shadowProcesses.RepeatedServerRequest.INTERVAL_BETWEEN_REPEATED_REQUEST} секунд"
            Window.info_label.config(text = text_info_timer)
            if shadowProcesses.RepeatedServerRequest.counter != 0:
                shadowProcesses.RepeatedServerRequest.counter = round(shadowProcesses.RepeatedServerRequest.counter-0.1,1)
            else:
                shadowProcesses.RepeatedServerRequest.counter = shadowProcesses.RepeatedServerRequest.INTERVAL_BETWEEN_REPEATED_REQUEST
                print(f"Cycle server request #{shadowProcesses.RepeatedServerRequest.numberofRequest} is runned")
                BybitExchange.Orderbook.getOrderbook()
                Graph.Orderbook.reload()
                shadowProcesses.RepeatedServerRequest.numberofRequest += 1


        @staticmethod
        def run():
            threading.Timer(shadowProcesses.RepeatedServerRequest.INTERVAL_BETWEEN_UPDATE_TIMER_LABEL, shadowProcesses.RepeatedServerRequest.run).start()
            shadowProcesses.RepeatedServerRequest.serverRequest()