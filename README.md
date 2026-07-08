# 🏋️ FitBot — фітнес-помічник у Telegram

Бот для розрахунку BMI/TDEE/БЖУ, планів тренувань, трекера ваги з графіком
прогресу та фото/відео прогресу тіла (з автоматичним порівнянням "до/після").

## Можливості

- 📊 Розрахунок BMI, базового обміну (BMR), денної норми калорій (TDEE) та БЖУ
- 🏋️ Плани тренувань (вдома / зал, початківець / середній рівень)
- ⚖️ Трекер ваги з графіком прогресу
- 📸 Фото/відео прогресу тіла + автоматичне порівняння першого й останнього фото поруч

## Технології

Python 3.11+, aiogram 3, SQLite (aiosqlite), matplotlib, Pillow.

## Запуск локально

1. Встанови залежності:
   ```bash
   pip install -r requirements.txt
   ```
2. Створи бота через [@BotFather](https://t.me/BotFather) і отримай токен.
3. Скопіюй `.env.example` у `.env` і встав токен:
   ```bash
   cp .env.example .env
   ```
4. Запусти бота:
   ```bash
   python bot.py
   ```

## Деплой на Railway

1. Створи новий репозиторій на GitHub і залий туди цей код:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: FitBot"
   git branch -M main
   git remote add origin https://github.com/ВАШ_НІК/fitbot.git
   git push -u origin main
   ```
2. Зайди на [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**.
3. Обери репозиторій `fitbot`.
4. У розділі **Variables** додай змінну оточення:
   - `BOT_TOKEN` = токен від @BotFather
5. Railway автоматично визначить `Procfile` і запустить процес `worker: python bot.py`.
6. Готово — бот працює 24/7.

> Файл БД (`fitbot.db`) створюється автоматично при першому запуску. На
> Railway дані зберігаються, поки контейнер не перестворюється "з нуля" —
> для продакшн-навантаження варто підключити окремий постійний диск
> (Railway Volumes) або перейти на PostgreSQL.

## Структура проєкту

```
fitbot/
├── bot.py              # точка входу
├── config.py            # конфігурація (токен, шлях до БД)
├── database.py           # робота з SQLite
├── calculators.py        # BMI/BMR/TDEE/БЖУ розрахунки
├── workouts.py           # шаблони тренувальних планів
├── states.py             # FSM-стани
├── keyboards.py          # inline-клавіатури
├── charts.py              # генерація графіка ваги (matplotlib)
├── handlers/
│   ├── start.py          # /start та головне меню
│   ├── profile.py        # опитування + розрахунок показників
│   ├── workout.py        # вибір і показ плану тренувань
│   ├── progress.py       # запис ваги + графік прогресу
│   └── photos.py         # фото/відео прогресу + порівняння
├── requirements.txt
├── Procfile              # для Railway/Heroku
├── .env.example
└── .gitignore
```

## Наступні кроки для монетизації

- Додати оплату через Telegram Stars (безкоштовні генерації → преміум)
- Персоналізовані плани тренувань через Claude/GPT API замість статичних шаблонів
- Нагадування про тренування/зважування через `apscheduler` або Railway Cron
- Перехід з SQLite на PostgreSQL для надійності при масштабуванні
