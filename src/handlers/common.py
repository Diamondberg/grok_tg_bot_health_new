# src/handlers/common.py
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

router = Router()

@router.message(Command(commands=["start"]))
async def start_command(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Общий тест")]
        ],
        resize_keyboard=True
    )
    await message.answer(
        "Добро пожаловать в HealthBot!\n"
        "Я помогу вам пройти тест на здоровье.\n"
        "Нажмите 'Общий тест', чтобы начать.",
        reply_markup=keyboard
    )

@router.message(Command(commands=["cancel"]))
async def cancel_command(message: Message):
    await message.answer("Действие отменено. Нажмите 'Общий тест', чтобы начать заново.")