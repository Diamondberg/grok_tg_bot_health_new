# src/handlers/client.py
from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.data.questions import QUESTIONS, SYSTEMS
from src.states.states import TestStates
import logging

router = Router()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.message(lambda message: message.text == "Общий тест")
async def start_test(message: Message, state: FSMContext):
    logger.info(f"Starting test for user {message.from_user.id}, is_bot: {message.from_user.is_bot}")
    scores = {system: 0 for system in SYSTEMS}
    await state.update_data(question_idx=0, scores=scores, answers=[])
    await state.set_state(TestStates.QUESTION)
    await ask_question(message.from_user.id, 0, message, state)

async def ask_question(user_id: int, question_idx: int, message: Message, state: FSMContext):
    logger.info(f"Asking question {question_idx+1}/{len(QUESTIONS)} for user {user_id}")
    if question_idx >= len(QUESTIONS):
        logger.info(f"Test completed for user {user_id}, calling show_results")
        state_data = await state.get_data()
        logger.info(f"State data before results: {state_data}")
        callback = state_data.get("last_callback")
        if callback:
            await show_results(callback, state)
        else:
            logger.error(f"No last_callback in state for user {user_id}, cannot show results")
            await message.bot.send_message(user_id, "Ошибка: не удалось показать результаты. Попробуйте заново с /start.")
        await state.clear()
        logger.info(f"State cleared for user {user_id}")
        return
    
    progress = int((question_idx + 1) / len(QUESTIONS) * 10)
    progress_bar = "█" * progress + " " * (10 - progress)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data=f"answer_yes_{question_idx}")],
        [InlineKeyboardButton(text="Нет", callback_data=f"answer_no_{question_idx}")]
    ])
    await message.bot.send_message(
        user_id,
        f"Вопрос {question_idx+1}/{len(QUESTIONS)}: {QUESTIONS[question_idx]['text']}\n"
        f"Осталось: {len(QUESTIONS)-question_idx-1}\nПрогресс: [{progress_bar} {progress*10}%]",
        reply_markup=keyboard
    )
    logger.info(f"Sent question {question_idx+1} to user {user_id}")

@router.callback_query(TestStates.QUESTION, lambda c: c.data.startswith("answer_"))
async def process_answer(callback: CallbackQuery, state: FSMContext):
    try:
        logger.info(f"Processing answer for user {callback.from_user.id}, is_bot: {callback.from_user.is_bot}")
        answer = callback.data.split("_")[1]
        question_idx = int(callback.data.split("_")[2])
        
        user_data = await state.get_data()
        answers = user_data.get("answers", [])
        scores = user_data.get("scores", {})
        
        # Сохраняем ответ
        answers.append({"question": QUESTIONS[question_idx]["text"], "answer": answer})
        
        # Добавляем балл, если ответ "Да"
        if answer == "yes":
            system = QUESTIONS[question_idx]["system"]
            scores[system] += 1
        
        # Обновляем данные
        next_idx = question_idx + 1
        await state.update_data(question_idx=next_idx, scores=scores, answers=answers, last_callback=callback)
        logger.info(f"Processed answer for question {question_idx+1} (answer: {answer}) for user {callback.from_user.id}, moving to question {next_idx+1}")
        logger.info(f"Current scores: {scores}")
        
        # Задаём следующий вопрос или завершаем
        await ask_question(callback.from_user.id, next_idx, callback.message, state)
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in process_answer for user {callback.from_user.id}: {str(e)}")
        await callback.message.bot.send_message(
            callback.from_user.id,
            "Произошла ошибка. Попробуйте начать тест заново с /start."
        )
        await state.clear()
        await callback.answer()

async def show_results(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    scores = state_data.get("scores", {})
    
    logger.info(f"Showing results for user {callback.from_user.id}, scores: {scores}, is_bot: {callback.from_user.is_bot}")
    
    # Формируем результат
    results_text = "🎉 Ваши результаты:\n"
    for system, score in scores.items():
        status = "Великолепно" if score <= 2 else "Хорошо" if score <= 5 else "Удовлетворительно" if score <= 9 else "Плохо"
        results_text += f"- {system}: {status} ({score} баллов) {'⚠️' if score >= 6 else '✅'}\n"
    
    try:
        await callback.message.bot.send_message(callback.from_user.id, results_text)
        logger.info(f"Results sent to user {callback.from_user.id}")
    except Exception as e:
        logger.error(f"Failed to send results to user {callback.from_user.id}: {str(e)}")
        await callback.message.bot.send_message(
            callback.from_user.id,
            "Не удалось отправить результаты. Возможно, ваш аккаунт ограничен. Попробуйте другой аккаунт или начните заново с /start."
        )