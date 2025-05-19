# bot.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from src.handlers.common import router as common_router
from src.handlers.client import router as client_router
from dotenv import load_dotenv
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Загружаем .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(common_router)
    dp.include_router(client_router)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())