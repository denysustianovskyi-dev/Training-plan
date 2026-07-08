ACTIVITY_FACTORS = {
    "sedentary": 1.2,     # сидяча робота, без спорту
    "light": 1.375,       # тренування 1-3 рази/тиждень
    "moderate": 1.55,     # тренування 3-5 разів/тиждень
    "active": 1.725,      # тренування 6-7 разів/тиждень
    "very_active": 1.9,   # фізична робота + тренування
}

ACTIVITY_LABELS = {
    "sedentary": "Сидячий спосіб життя",
    "light": "Легка активність (1-3 р/тиж)",
    "moderate": "Середня активність (3-5 р/тиж)",
    "active": "Висока активність (6-7 р/тиж)",
    "very_active": "Дуже висока активність",
}

GOAL_LABELS = {
    "lose": "Схуднення",
    "maintain": "Підтримка ваги",
    "gain": "Набір маси",
}


def calc_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Недостатня вага"
    elif bmi < 25:
        return "Норма"
    elif bmi < 30:
        return "Надлишкова вага"
    else:
        return "Ожиріння"


def calc_bmr(gender: str, weight_kg: float, height_cm: float, age: int) -> float:
    """Формула Міффліна-Сан Жеора"""
    if gender == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def calc_tdee(bmr: float, activity: str) -> int:
    factor = ACTIVITY_FACTORS.get(activity, 1.2)
    return round(bmr * factor)


def calc_target_calories(tdee: int, goal: str) -> int:
    if goal == "lose":
        return round(tdee - tdee * 0.2)
    elif goal == "gain":
        return round(tdee + tdee * 0.15)
    return tdee


def calc_macros(target_cal: int, weight_kg: float, goal: str) -> dict:
    if goal == "lose":
        protein_g = round(weight_kg * 2.0)
    elif goal == "gain":
        protein_g = round(weight_kg * 1.8)
    else:
        protein_g = round(weight_kg * 1.6)

    fat_g = round((target_cal * 0.25) / 9)
    protein_cal = protein_g * 4
    fat_cal = fat_g * 9
    carbs_cal = max(target_cal - protein_cal - fat_cal, 0)
    carbs_g = round(carbs_cal / 4)

    return {"protein": protein_g, "fat": fat_g, "carbs": carbs_g}


def full_report(gender, age, height, weight, activity, goal) -> dict:
    bmi = calc_bmi(weight, height)
    bmr = calc_bmr(gender, weight, height, age)
    tdee = calc_tdee(bmr, activity)
    target_cal = calc_target_calories(tdee, goal)
    macros = calc_macros(target_cal, weight, goal)
    return {
        "bmi": bmi,
        "bmi_category": bmi_category(bmi),
        "bmr": round(bmr),
        "tdee": tdee,
        "target_cal": target_cal,
        "macros": macros,
    }
