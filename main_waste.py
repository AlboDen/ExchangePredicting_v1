import os
import time
from pybit.unified_trading import HTTP
from pybit.exceptions import InvalidRequestError, FailedRequestError

from network.BybitExchange import BybitExchange

# session = HTTP(
#     testnet=False,
#     api_key="BYBIT_API_KEY",
#     api_secret="BYBIT_API_SECRET",
# )

symbol = "XRPUSDT"
side = "Buy"
qty = 7.0
price = BybitExchange.Klines.get_current_price("XRPUSDT")

# 1. Ставим лимитный ордер
try:
    resp = BybitExchange.session_trade.place_order(
        category="spot",
        symbol=symbol,
        side=side,
        orderType="Limit",
        qty=qty,
        price=price,
    )
    order_id = resp["result"]["orderId"]
    print("Ордер выставлен:", order_id)
except (InvalidRequestError, FailedRequestError) as e:
    print("Ошибка выставления:", e)
    raise

# 2. Ждём 3 секунды и отменяем, если не закрылся
time.sleep(3)

try:
    # Проверяем статус и отменяем только если активен
    status_resp = BybitExchange.session_trade.get_trade_list(category="spot", symbol=symbol)
    orders = status_resp["result"]["list"]
    active_order = next((o for o in orders if o["orderId"] == order_id and o["orderStatus"] != "Filled"), None)

    if active_order:
        cancel_resp = BybitExchange.session_trade.cancel_order(
            category="spot",
            symbol=symbol,
            orderId=order_id,
        )
        print("Ордер отменён через 3 сек:", cancel_resp)
    else:
        print("Ордер уже исполнился!")
except (InvalidRequestError, FailedRequestError) as e:
    print("Ошибка проверки/отмены:", e)
