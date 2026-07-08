from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from calculators import ACTIVITY_LABELS, GOAL_LABELS
from workouts import LOCATION_LABELS, LEVEL_LABELS


def main_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="📊 Мій профіль / Розрахунок", callback_data="menu:profile")
    b.button(text="🏋️ План тренувань", callback_data="menu:workout")
    b.button(text="⚖️ Записати вагу", callback_data="menu:logweight")
    b.button(text="📈 Мій прогрес (вага)", callback_data="menu:progress")
    b.button(text="📸 Фото/відео прогресу", callback_data="menu:photos")
    b.adjust(1)
    return b.as_markup()


def photos_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="📤 Зняти / додати фото чи відео", callback_data="photos:add")
    b.button(text="🖼 Переглянути галерею", callback_data="photos:view")
    b.button(text="🔀 Порівняти перше і останнє", callback_data="photos:compare")
    b.button(text="⬅️ Головне меню", callback_data="menu:main")
    b.adjust(1)
    return b.as_markup()


def gender_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="Чоловіча", callback_data="gender:male")
    b.button(text="Жіноча", callback_data="gender:female")
    b.adjust(2)
    return b.as_markup()


def activity_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for key, label in ACTIVITY_LABELS.items():
        b.button(text=label, callback_data=f"activity:{key}")
    b.adjust(1)
    return b.as_markup()


def goal_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for key, label in GOAL_LABELS.items():
        b.button(text=label, callback_data=f"goal:{key}")
    b.adjust(1)
    return b.as_markup()


def location_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for key, label in LOCATION_LABELS.items():
        b.button(text=label, callback_data=f"location:{key}")
    b.adjust(1)
    return b.as_markup()


def level_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for key, label in LEVEL_LABELS.items():
        b.button(text=label, callback_data=f"level:{key}")
    b.adjust(1)
    return b.as_markup()


def back_to_menu_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="⬅️ Головне меню", callback_data="menu:main")
    return b.as_markup()
