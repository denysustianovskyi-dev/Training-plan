from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards import location_kb, level_kb, back_to_menu_kb
from states import WorkoutForm
from workouts import get_plan, LOCATION_LABELS, LEVEL_LABELS

router = Router()


@router.callback_query(F.data == "menu:workout")
async def workout_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WorkoutForm.location)
    await callback.message.edit_text(
        "🏋️ Де плануєш тренуватись?", reply_markup=location_kb()
    )
    await callback.answer()


@router.callback_query(WorkoutForm.location, F.data.startswith("location:"))
async def workout_location(callback: CallbackQuery, state: FSMContext):
    location = callback.data.split(":")[1]
    await state.update_data(location=location)
    await state.set_state(WorkoutForm.level)
    await callback.message.edit_text("Який у тебе рівень підготовки?", reply_markup=level_kb())
    await callback.answer()


@router.callback_query(WorkoutForm.level, F.data.startswith("level:"))
async def workout_level(callback: CallbackQuery, state: FSMContext):
    level = callback.data.split(":")[1]
    data = await state.update_data(level=level)
    await state.clear()

    plan = get_plan(data["location"], data["level"])
    if not plan:
        await callback.message.edit_text(
            "На жаль, для цієї комбінації плану ще немає 🙁", reply_markup=back_to_menu_kb()
        )
        await callback.answer()
        return

    text = f"🏋️ {plan['title']}\n\n"
    for day_title, exercises in plan["days"]:
        text += f"<b>{day_title}</b>\n"
        for ex in exercises:
            text += f"• {ex}\n"
        text += "\n"
    text += "💡 Відпочинок між підходами: 60-90 сек. Розминка 5-10 хв перед тренуванням обов'язкова."

    await callback.message.edit_text(text, reply_markup=back_to_menu_kb(), parse_mode="HTML")
    await callback.answer()
