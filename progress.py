from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from charts import build_weight_chart
from database import log_weight, get_weight_history, get_profile
from keyboards import back_to_menu_kb
from states import WeightLogForm

router = Router()


@router.callback_query(F.data == "menu:logweight")
async def logweight_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WeightLogForm.weight)
    await callback.message.edit_text(
        "⚖️ Введи свою поточну вагу в кг, наприклад: 68.5"
    )
    await callback.answer()


@router.message(WeightLogForm.weight)
async def logweight_save(message: Message, state: FSMContext):
    try:
        weight = float(message.text.strip().replace(",", "."))
        assert 30 <= weight <= 300
    except (ValueError, AssertionError):
        await message.answer("Введи вагу у кг числом від 30 до 300, наприклад: 68.5")
        return

    profile = await get_profile(message.from_user.id)
    if not profile:
        await message.answer(
            "Спочатку заповни профіль (кнопка «Мій профіль») — так я зможу "
            "рахувати твої показники правильно."
        )
        await state.clear()
        return

    await log_weight(message.from_user.id, weight)
    await state.clear()
    await message.answer(
        f"✅ Записано: {weight} кг. Переглянь прогрес кнопкою нижче 👇",
        reply_markup=back_to_menu_kb(),
    )


@router.callback_query(F.data == "menu:progress")
async def show_progress(callback: CallbackQuery):
    history = await get_weight_history(callback.from_user.id)
    if len(history) < 2:
        await callback.message.edit_text(
            "Поки що замало даних для графіка. Записуй вагу регулярно "
            "(раз на кілька днів) — і тут з'явиться графік прогресу 📈",
            reply_markup=back_to_menu_kb(),
        )
        await callback.answer()
        return

    chart = build_weight_chart(history)
    first_w = history[0]["weight"]
    last_w = history[-1]["weight"]
    diff = round(last_w - first_w, 1)
    sign = "+" if diff > 0 else ""

    await callback.answer()
    await callback.message.answer_photo(
        chart,
        caption=(
            f"📈 Твій прогрес ваги\n\n"
            f"Початок: {first_w} кг → Зараз: {last_w} кг\n"
            f"Зміна: {sign}{diff} кг за {len(history)} записів"
        ),
        reply_markup=back_to_menu_kb(),
    )
