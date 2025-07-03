from fastapi import FastAPI, Request, HTTPException
from pybit.unified_trading import HTTP
from loguru import logger
import os

API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
TESTNET = os.environ.get("TESTNET", "True") == "True"
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")
QUANTITY = 0.001  # число, а не строка

# Подключение к Bybit (спотовый рынок)
session = HTTP(testnet=TESTNET, api_key=API_KEY, api_secret=API_SECRET)

app = FastAPI()

logger.add("webhook_logs.log", rotation="10 MB", retention="7 days", compression="zip")


@app.get("/")
def test():
    return {"status": "test"}


@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        logger.info(f"Получен сигнал: {data}")

        if data.get("secret") != WEBHOOK_SECRET:
            logger.warning("Попытка несанкционированного доступа.")
            raise HTTPException(status_code=403, detail="Запрещено")

        action = data.get("action")
        symbol = data.get("symbol", "BTCUSDT")

        if action not in ["buy", "sell"]:
            logger.warning(f"Недопустимое действие: {action}")
            return {"status": "Недопустимое действие. Разрешены только buy и sell."}

        try:
            if action == "buy":
                order = session.place_order(
                    category="spot",
                    symbol=symbol,
                    side="Buy",
                    order_type="Market",
                    qty=QUANTITY
                )
                logger.info(f"Ордер на покупку отправлен: {order}")
                return {"status": "Buy order sent", "order": order}

            elif action == "sell":
                order = session.place_order(
                    category="spot",
                    symbol=symbol,
                    side="Sell",
                    order_type="Market",
                    qty=QUANTITY
                )
                logger.info(f"Ордер на продажу отправлен: {order}")
                return {"status": "Sell order sent", "order": order}

        except Exception as e:
            logger.exception(f"Ошибка при отправке ордера: {e}")
            return {"status": "Ошибка при отправке ордера", "detail": str(e)}

    except Exception as e:
        logger.exception(f"Ошибка сервера: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
