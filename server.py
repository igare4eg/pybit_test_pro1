from fastapi import FastAPI, Request, HTTPException
from pybit.unified_trading import HTTP
from loguru import logger
import os

API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
TESTNET = os.environ.get("TESTNET", "True") == "True"
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET")
QUANTITY = "0.001"

# Подключение к Bybit
session = HTTP(testnet=TESTNET, api_key=API_KEY, api_secret=API_SECRET)

app = FastAPI()

# Настройка логов
logger.add("webhook_logs.log", rotation="10 MB", retention="7 days", compression="zip")

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

        if action == "buy":
            order = session.place_order(
                category="linear",
                symbol=symbol,
                side="Buy",
                order_type="Market",
                qty=QUANTITY
            )
            logger.info(f"Ордер на покупку отправлен: {order}")
            return {"status": "Buy order sent", "order": order}

        elif action == "sell":
            order = session.place_order(
                category="linear",
                symbol=symbol,
                side="Sell",
                order_type="Market",
                qty=QUANTITY
            )
            logger.info(f"Ордер на продажу отправлен: {order}")
            return {"status": "Sell order sent", "order": order}

        logger.info("Неизвестное действие.")
        return {"status": "No action taken"}

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")