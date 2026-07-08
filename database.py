import aiosqlite
from config import DB_PATH

CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    gender TEXT,
    age INTEGER,
    height REAL,
    weight REAL,
    activity TEXT,
    goal TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

CREATE_WEIGHT_LOG = """
CREATE TABLE IF NOT EXISTS weight_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    weight REAL NOT NULL,
    logged_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
"""

CREATE_PHOTOS = """
CREATE TABLE IF NOT EXISTS progress_photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    file_id TEXT NOT NULL,
    media_type TEXT NOT NULL,
    logged_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
)
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_USERS)
        await db.execute(CREATE_WEIGHT_LOG)
        await db.execute(CREATE_PHOTOS)
        await db.commit()


async def upsert_profile(user_id, username, gender, age, height, weight, activity, goal):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (user_id, username, gender, age, height, weight, activity, goal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                gender=excluded.gender,
                age=excluded.age,
                height=excluded.height,
                weight=excluded.weight,
                activity=excluded.activity,
                goal=excluded.goal
            """,
            (user_id, username, gender, age, height, weight, activity, goal),
        )
        await db.commit()
    # перший запис ваги при створенні профілю
    await log_weight(user_id, weight)


async def get_profile(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def log_weight(user_id: int, weight: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO weight_log (user_id, weight) VALUES (?, ?)", (user_id, weight)
        )
        await db.execute("UPDATE users SET weight=? WHERE user_id=?", (weight, user_id))
        await db.commit()


async def get_weight_history(user_id: int, limit: int = 60):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT weight, logged_at FROM weight_log
            WHERE user_id=? ORDER BY logged_at DESC LIMIT ?
            """,
            (user_id, limit),
        ) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows][::-1]


async def add_photo(user_id: int, file_id: str, media_type: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO progress_photos (user_id, file_id, media_type) VALUES (?, ?, ?)",
            (user_id, file_id, media_type),
        )
        await db.commit()


async def get_photos(user_id: int, limit: int = 50):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT file_id, media_type, logged_at FROM progress_photos
            WHERE user_id=? ORDER BY logged_at ASC LIMIT ?
            """,
            (user_id, limit),
        ) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]
