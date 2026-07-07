from aiogram.fsm.state import State, StatesGroup


class ProfileForm(StatesGroup):
    gender = State()
    age = State()
    height = State()
    weight = State()
    activity = State()
    goal = State()


class WeightLogForm(StatesGroup):
    weight = State()


class WorkoutForm(StatesGroup):
    location = State()
    level = State()


class PhotoForm(StatesGroup):
    waiting = State()
