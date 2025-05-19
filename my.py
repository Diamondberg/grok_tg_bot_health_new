from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio

# Твой токен от BotFather в Telegram
BOT_TOKEN = "6548569648:AAERW8O801gySZ7m8AJPpKTEQiuejKHxmO0"  # Замени на реальный токен

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я эхо-бот. Пиши мне что угодно, и я повторю!")

# Обработчик всех сообщений (эхо)
@dp.message()
async def echo(message: types.Message):
    await message.answer(message.text)

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())