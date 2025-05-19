from aiogram.fsm.state import State, StatesGroup

class TestStates(StatesGroup):
    QUESTION = State()  # Состояние для вопросов