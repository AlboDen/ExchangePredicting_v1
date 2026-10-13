"""
trader = BybitSpotLimiter(
    api_key="ТВОЙ_API_KEY",
    private_key="ТВОЙ_SECRET_KEY",
    testnet=True  # обязательно используй testnet для тестов
)

try:
    # Выставляем лимитный ордер
    resp = trader.place_limit_order("BTCUSDT", "Buy", 0.001, 42000)
    order_id = resp["result"]["orderId"]
    print("Ордер создан, ID:", order_id)

    # Отменяем один ордер
    cancel_resp = trader.cancel_order(order_id=order_id, symbol="BTCUSDT")
    print("Ордер отменён:", cancel_resp)

    # Либо сразу закрываем все активные ордера по символу
    # all_closed = trader.close_all_orders("BTCUSDT")
    # print("Все ордера отменены:", all_closed)

except Exception as e:
    print("Ошибка:", e)

"""
from pybit.unified_trading import HTTP
from typing import Any, Dict

class BybitSpotLimiter:
    """
    Универсальный класс для спотовых лимитных ордеров на Bybit.
    Автоматически подбирает правильное имя параметра для ключа (secret/private_key)
    в зависимости от версии pybit. Без JSON, без БД — только API.
    """

    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        :param api_key: API Key от Bybit
        :param api_secret: Secret Key (в коде называем api_secret, а внутри подставим правильное имя)
        :param testnet: True для тестовой сети, False для реальной
        """
        # Определяем, какое имя параметра ожидает HTTP() в этой версии pybit
        # Проверяем через inspect или просто пробуем передать оба варианта и смотрим, какой сработает
        # Но самый простой и надёжный способ — проверить сигнатуру конструктора
        import inspect
        sig = inspect.signature(HTTP.__init__)
        params = list(sig.parameters.keys())

        # В старых версиях pybit: параметр 'secret'
        # В новых (>=3.x): параметр 'private_key'
        if "private_key" in params:
            init_kwargs = {
                "api_key": api_key,
                "api_secret": api_secret,
                "testnet": testnet,
            }
        elif "secret" in params:
            init_kwargs = {
                "api_key": api_key,
                "api_secret": api_secret,
                "testnet": testnet,
            }
        else:
            # fallback: пробуем private_key по умолчанию (стандарт для актуальных версий)
            init_kwargs = {
                "api_key": api_key,
                "api_secret": api_secret,
                "testnet": testnet,
            }

        self.client = HTTP(**init_kwargs)
        self.testnet = testnet

    def place_limit_order(
        self,
        symbol: str,
        side: str,
        qty: float,
        price: float,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """Выставляет лимитный ордер. Возвращает полный ответ API."""
        if side not in ("Buy", "Sell"):
            raise ValueError("side должен быть 'Buy' или 'Sell'")

        params = {
            "category": "spot",
            "symbol": symbol,
            "side": side,
            "orderType": "Limit",
            "qty": str(qty),
            "price": str(price),
            "timeInForce": time_in_force,
        }

        resp = self.client.place_order(**params)
        if resp.get("retCode") != 0:
            raise RuntimeError(f"Ошибка создания ордера: {resp}")
        return resp

    def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Отменяет один ордер по order_id. Возвращает ответ API."""
        params = {
            "category": "spot",
            "symbol": symbol,
            "orderId": order_id,
        }
        resp = self.client.cancel_order(**params)
        if resp.get("retCode") != 0:
            raise RuntimeError(f"Ошибка отмены ордера: {resp}")
        return resp

    def close_all_orders(self, symbol: str) -> Dict[str, Any]:
        """Массово отменяет все активные ордера по символу. Возвращает ответ API."""
        params = {
            "category": "spot",
            "symbol": symbol,
        }
        resp = self.client.cancel_all(**params)
        if resp.get("retCode") != 0:
            raise RuntimeError(f"Ошибка массовой отмены ордеров: {resp}")
        return resp
