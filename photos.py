import io
from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from PIL import Image, ImageDraw, ImageFont

from database import add_photo, get_photos
from states import PhotoForm
from keyboards import photos_menu_kb, back_to_menu_kb

router = Router()


def _fmt_date(raw: str) -> str:
    try:
        dt = datetime.strptime(raw[:19], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        dt = datetime.fromisoformat(raw)
    return dt.strftime("%d.%m.%Y")


@router.callback_query(F.data == "menu:photos")
async def photos_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "📸 Фото/відео прогресу тіла\n\n"
        "Знімай фото чи коротке відео раз на 1-2 тижні (бажано в одному "
        "одязі, освітленні та ракурсі) — так буде найкраще видно зміни "
        "через місяць.",
        reply_markup=photos_menu_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "photos:add")
async def photos_add(callback: CallbackQuery, state: FSMContext):
    await state.set_state(PhotoForm.waiting)
    await callback.message.edit_text(
        "📤 Надішли фото або коротке відео тіла прямо в цей чат.\n\n"
        "Можеш зняти нове (кнопка 📎 → камера) або вибрати з галереї.",
        reply_markup=back_to_menu_kb(),
    )
    await callback.answer()


@router.message(PhotoForm.waiting, F.photo)
async def photo_received(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await add_photo(message.from_user.id, file_id, "photo")
    await state.clear()
    await message.answer(
        "✅ Фото збережено! Через 2-4 тижні додай ще одне — і зможеш "
        "порівняти зміни кнопкою «Порівняти перше і останнє».",
        reply_markup=photos_menu_kb(),
    )


@router.message(PhotoForm.waiting, F.video)
async def video_received(message: Message, state: FSMContext):
    file_id = message.video.file_id
    await add_photo(message.from_user.id, file_id, "video")
    await state.clear()
    await message.answer(
        "✅ Відео збережено! Переглянути всі записи можна в галереї.",
        reply_markup=photos_menu_kb(),
    )


@router.message(PhotoForm.waiting)
async def photo_wrong_content(message: Message):
    await message.answer("Надішли, будь ласка, саме фото 📷 або відео 🎥.")


@router.callback_query(F.data == "photos:view")
async def photos_view(callback: CallbackQuery):
    photos = await get_photos(callback.from_user.id)
    if not photos:
        await callback.message.edit_text(
            "У тебе ще немає збережених фото чи відео. Додай перше!",
            reply_markup=photos_menu_kb(),
        )
        await callback.answer()
        return

    await callback.answer()
    await callback.message.answer(f"🖼 Твоя галерея прогресу ({len(photos)}):")
    for item in photos:
        caption = f"📅 {_fmt_date(item['logged_at'])}"
        if item["media_type"] == "photo":
            await callback.message.answer_photo(item["file_id"], caption=caption)
        else:
            await callback.message.answer_video(item["file_id"], caption=caption)
    await callback.message.answer("Меню:", reply_markup=photos_menu_kb())


@router.callback_query(F.data == "photos:compare")
async def photos_compare(callback: CallbackQuery):
    photos = [p for p in await get_photos(callback.from_user.id) if p["media_type"] == "photo"]

    if len(photos) < 2:
        await callback.message.edit_text(
            "Для порівняння потрібно щонайменше 2 фото. Додай ще одне — "
            "і повертайся сюди 🙂",
            reply_markup=photos_menu_kb(),
        )
        await callback.answer()
        return

    first, last = photos[0], photos[-1]
    bot = callback.bot

    first_bytes = await bot.download(first["file_id"])
    last_bytes = await bot.download(last["file_id"])

    img1 = Image.open(first_bytes).convert("RGB")
    img2 = Image.open(last_bytes).convert("RGB")

    target_h = 800
    def resize(img):
        ratio = target_h / img.height
        return img.resize((int(img.width * ratio), target_h))

    img1 = resize(img1)
    img2 = resize(img2)

    label_h = 50
    gap = 10
    canvas = Image.new(
        "RGB", (img1.width + img2.width + gap, target_h + label_h), "white"
    )
    canvas.paste(img1, (0, label_h))
    canvas.paste(img2, (img1.width + gap, label_h))

    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28
        )
    except OSError:
        font = ImageFont.load_default()

    draw.text((10, 10), f"ДО: {_fmt_date(first['logged_at'])}", fill="black", font=font)
    draw.text(
        (img1.width + gap + 10, 10),
        f"ПІСЛЯ: {_fmt_date(last['logged_at'])}",
        fill="black",
        font=font,
    )

    buf = io.BytesIO()
    canvas.save(buf, format="JPEG", quality=90)
    buf.seek(0)

    await callback.answer()
    await callback.message.answer_photo(
        BufferedInputFile(buf.read(), filename="compare.jpg"),
        caption="🔀 Порівняння: перше і останнє фото",
        reply_markup=photos_menu_kb(),
    )
