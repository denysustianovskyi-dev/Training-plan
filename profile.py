from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from calculators import full_report, GOAL_LABELS
from database import get_profile, upsert_profile
from keyboards import gender_kb, activity_kb, goal_kb, back_to_menu_kb
from states import ProfileForm

router = Router()


@router.callback_query(F.data == "menu:profile")
async def profile_start(callback: CallbackQuery, state: FSMContext):
    profile = await get_profile(callback.from_user.id)
    if profile:
        report = full_report(
            profile["gender"],
            profile["age"],
            profile["height"],
            profile["weight"],
            profile["activity"],
            profile["goal"],
        )
        text = _report_text(profile, report)
        text += "\n\nХочеш оновити дані? Просто пройди опитування ще раз."

        kb = InlineKeyboardBuilder()
        kb.button(text="🔄 Оновити дані", callback_data="profile:restart")
        kb.button(text="⬅️ Головне меню", callback_data="menu:main")
        kb.adjust(1)

        await callback.message.edit_text(text, reply_markup=kb.as_markup())
        await callback.answer()
        return

    await state.set_state(ProfileForm.gender)
    await callback.message.edit_text(
        "Розрахуємо твої показники 📊\n\nОбери стать:", reply_markup=gender_kb()
    )
    await callback.answer()


@router.callback_query(F.data == "profile:restart")
async def profile_restart(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ProfileForm.gender)
    await callback.message.edit_text("Обери стать:", reply_markup=gender_kb())
    await callback.answer()


@router.callback_query(ProfileForm.gender, F.data.startswith("gender:"))
async def set_gender(callback: CallbackQuery, state: FSMContext):
    gender = callback.data.split(":")[1]
    await state.update_data(gender=gender)
    await state.set_state(ProfileForm.age)
    await callback.message.edit_text("Скільки тобі років?")
    await callback.answer()


@router.message(ProfileForm.age)
async def set_age(message: Message, state: FSMContext):
    try:
        age = int(message.text.strip())
        assert 10 <= age <= 100
    except (ValueError, AssertionError):
        await message.answer("Введи вік числом від 10 до 100, наприклад: 25")
        return
    await state.update_data(age=age)
    await state.set_state(ProfileForm.height)
    await message.answer("Який у тебе зріст у см? Наприклад: 175")


@router.message(ProfileForm.height)
async def set_height(message: Message, state: FSMContext):
    try:
        height = float(message.text.strip().replace(",", "."))
        assert 100 <= height <= 250
    except (ValueError, AssertionError):
        await message.answer("Введи зріст у см числом від 100 до 250, наприклад: 175")
        return
    await state.update_data(height=height)
    await state.set_state(ProfileForm.weight)
    await message.answer("Яка у тебе вага у кг? Наприклад: 70.5")


@router.message(ProfileForm.weight)
async def set_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text.strip().replace(",", "."))
        assert 30 <= weight <= 300
    except (ValueError, AssertionError):
        await message.answer("Введи вагу у кг числом від 30 до 300, наприклад: 70.5")
        return
    await state.update_data(weight=weight)
    await state.set_state(ProfileForm.activity)
    await message.answer("Який у тебе рівень активності?", reply_markup=activity_kb())


@router.callback_query(ProfileForm.activity, F.data.startswith("activity:"))
async def set_activity(callback: CallbackQuery, state: FSMContext):
    activity = callback.data.split(":")[1]
    await state.update_data(activity=activity)
    await state.set_state(ProfileForm.goal)
    await callback.message.edit_text("Яка твоя мета?", reply_markup=goal_kb())
    await callback.answer()


@router.callback_query(ProfileForm.goal, F.data.startswith("goal:"))
async def set_goal(callback: CallbackQuery, state: FSMContext):
    goal = callback.data.split(":")[1]
    data = await state.update_data(goal=goal)
    await state.clear()

    await upsert_profile(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        gender=data["gender"],
        age=data["age"],
        height=data["height"],
        weight=data["weight"],
        activity=data["activity"],
        goal=data["goal"],
    )

    report = full_report(
        data["gender"], data["age"], data["height"], data["weight"], data["activity"], data["goal"]
    )
    text = _report_text(data, report)
    await callback.message.edit_text(text, reply_markup=back_to_menu_kb())
    await callback.answer()


def _report_text(profile: dict, report: dict) -> str:
    macros = report["macros"]
    return (
        f"✅ Твої результати:\n\n"
        f"⚖️ BMI: {report['bmi']} ({report['bmi_category']})\n"
        f"🔥 Базовий обмін (BMR): {report['bmr']} ккал/добу\n"
        f"⚡ Денна норма (TDEE): {report['tdee']} ккал/добу\n\n"
        f"🎯 Мета: {GOAL_LABELS.get(profile['goal'], profile['goal'])}\n"
        f"📌 Цільова калорійність: {report['target_cal']} ккал/добу\n\n"
        f"БЖУ на день:\n"
        f"🥩 Білки: {macros['protein']} г\n"
        f"🧈 Жири: {macros['fat']} г\n"
        f"🍞 Вуглеводи: {macros['carbs']} г"
    )
