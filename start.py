from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from keyboards import main_menu_kb

router = Router()

WELCOME_TEXT = (
    "👋 Привіт! Я твій фітнес-помічник.\n\n"
    "Що я вмію:\n"
    "📊 Розрахувати BMI, норму калорій та БЖУ\n"
    "🏋️ Підібрати план тренувань\n"
    "⚖️ Вести трекер ваги з графіком прогресу\n\n"
    "Обери дію з меню нижче 👇"
)


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_kb())


@router.callback_query(F.data == "menu:main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(WELCOME_TEXT, reply_markup=main_menu_kb())
    await callback.answer()
