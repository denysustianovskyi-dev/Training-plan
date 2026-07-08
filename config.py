import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH", "fitbot.db")

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN не знайдено. Створіть файл .env на основі .env.example "
        "і вкажіть токен, отриманий у @BotFather."
    )
