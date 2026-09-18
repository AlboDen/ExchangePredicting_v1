import matplotlib.pyplot as plt
import numpy as np
import time
from pybit.unified_trading import HTTP

from regress import best_regression
from reg1 import best_regression as best_reg

plt.ion()  # Включаем интерактивный режим
fig, ax = plt.subplots()

# Инициализация графиков
# line1, = ax.plot([], [], 'o', color='blue', label='График 1')
# line2, = ax.plot([], [], 'o', color='red', label='График 2')


# Генерация и обновление каждые 3 секунды
while True:
    ax.clear()
    # Случайные точки
    print("s")
    session = HTTP(testnet=False)

    response = session.get_orderbook(
        category="spot",
        symbol="XRPUSDT",
        limit=3000,

    )
    orderbook = response["result"]

    # print("Заявки на покупку (bids):")
    buffer_list = []
    buffer_list1 = []

    # fig, ax = plt.subplots()
    # print("Asks: ")
    for price, size in orderbook["b"]:
        buffer_list.append(float(price))
        buffer_list1.append(float(size))
        # print(float(price), "\t", float(size))
    # line1.set_data(buffer_list1, buffer_list)
    # line1.set_data([0, 2, 6], [6, 9,2])
    ax.plot(buffer_list, buffer_list1, 'o', color='blue', label=f'Bids {len(buffer_list)}')
    max_x = np.max(buffer_list)
    # print("Bids: ")
    buffer_list = []
    buffer_list1 = []
    for price, size in orderbook["a"]:
        buffer_list.append(float(price))
        buffer_list1.append(float(size))
        # print(float(price), "\t", float(size))
    ax.plot(buffer_list, buffer_list1, 'o', color='red', label=f'Asks {len(buffer_list)}')

    min_x = np.min(buffer_list)
    mid_x = (min_x + max_x) / 2
    ax.axvline(mid_x, color='green', linestyle='--', alpha=0.7)
    # Автомасштабирование
    # ax.relim()
    # ax.autoscale_view()
    ax.set_xlabel("Volume")
    ax.set_xlabel("Price")
    # ax.set_ylim(0.00009,0.0001)
    # ax.set_xlim(mid_x-0.07, mid_x+0.07)
    ax.set_xlim(left=float(mid_x-0.01), right=float(mid_x+0.01))
    ax.set_ylim(0, 25000)
    print("ddddddddd")
    print( best_reg(buffer_list,buffer_list1) )
    buf = []
    match best_reg(buffer_list,buffer_list1)['model']:
        case "linear":
            for i in buffer_list:
                coefs = best_reg(buffer_list,buffer_list1)['coefficients']
                buf.append(coefs[0]*i+coefs[1])
        case "polynomial":
            match best_reg(buffer_list, buffer_list1)['degree']:
                case 3:
                    for i in buffer_list:
                        coefs = best_reg(buffer_list, buffer_list1)['coefficients']
                        buf.append(coefs[0] * i**3 + coefs[1] * i**2 + coefs[2] * i**1 + coefs[3])


            ax.plot(buffer_list, buf, 'o', color='red', label=f'Asks apps')
    # print(best_reg([0.0,1.0,2.0,3.0,4.0,5,6,7,8,9,10,11,12,13,14,15],
    #                       [1.0, 2.718281828, 7.389056099, 20.08553692, 54.59815003, 148,4131591,
# 403.4287935,
# 1096.633158,
# 2980.957987,
# 8103.083928,
# 22026.46579,
# 59874.14172,
# 162754.7914,
# 442413.392,
# 1202604.284]))

    ax.legend()
    # Пауза для обновления
    print("f", mid_x - 0.1)
    plt.draw()
    plt.pause(10)
    print("medium",mid_x)
