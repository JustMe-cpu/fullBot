import asyncio
import logging
import sqlite3
import os
import random
from aiogram import Bot, Dispatcher, types, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from dotenv import load_dotenv
from aiogram.types import FSInputFile
from parsers import fetch_currency, fetch_weather, fetch_joke, fetch_movies
from keyboards import main_keyboard, image_menu, joke_menu

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()

logging.basicConfig(level=logging.INFO)

DB_NAME = os.getenv("DB_NAME")

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()


cursor.execute("DROP TABLE IF EXISTS survey")

cursor.execute('''
CREATE TABLE survey (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    tg_id INTEGER,
    name TEXT,
    age INTEGER,
    subject TEXT,
    color TEXT,
    movie TEXT,
    q6 TEXT,
    q7 TEXT,
    q8 TEXT
)
''')

conn.commit()
@router.message(Command("start"))
async def start_handler(message: types.Message):
    user_name = message.from_user.first_name
    await message.answer(f"Привет, {user_name}! Выберите действие:", reply_markup=main_keyboard)

class Survey(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
    q6 = State()
    q7 = State()
    q8 = State()


@router.message(lambda message: message.text.lower() == "опрос")
async def start_survey(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(user_id=user_id, tg_id=message.from_user.id)
    cursor.execute("SELECT * FROM survey WHERE tg_id = ?", (message.from_user.id,))
    existing_data = cursor.fetchone()
    if existing_data:
        result_text = (
            f"📊 *Ваши предыдущие ответы:*\n"
            f"1️⃣ Имя: {existing_data[3]}\n"
            f"2️⃣ Возраст: {existing_data[4]}\n"
            f"3️⃣ Любимый предмет: {existing_data[5]}\n"
            f"4️⃣ Любимый цвет: {existing_data[6]}\n"
            f"5️⃣ Любимый фильм: {existing_data[7]}\n"
            f"6️⃣ {existing_data[8]}\n"
            f"7️⃣ {existing_data[9]}\n"
            f"8️⃣ {existing_data[10]}"
        )
        await message.answer("Вы уже проходили опрос! Вот ваши ответы:")
        await message.answer(result_text, parse_mode="Markdown")
        return
    await message.answer("1) Как вас зовут?")
    await state.set_state(Survey.q1)

@router.message(Survey.q1)
async def survey_q1(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("2) Сколько вам лет?")
    await state.set_state(Survey.q2)

@router.message(Survey.q2)
async def survey_q2(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("3) Какой ваш любимый школьный предмет?")
    await state.set_state(Survey.q3)

@router.message(Survey.q3)
async def survey_q3(message: types.Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await message.answer("4) Какой ваш любимый цвет?")
    await state.set_state(Survey.q4)

@router.message(Survey.q4)
async def survey_q4(message: types.Message, state: FSMContext):
    await state.update_data(color=message.text)
    await message.answer("5) Какой ваш любимый фильм?")
    await state.set_state(Survey.q5)

@router.message(Survey.q5)
async def survey_q5(message: types.Message, state: FSMContext):
    await state.update_data(movie=message.text)
    await message.answer("6) Вопрос на ваше усмотрение:")
    await state.set_state(Survey.q6)

@router.message(Survey.q6)
async def survey_q6(message: types.Message, state: FSMContext):
    await state.update_data(q6=message.text)
    await message.answer("7) Еще один вопрос:")
    await state.set_state(Survey.q7)

@router.message(Survey.q7)
async def survey_q7(message: types.Message, state: FSMContext):
    await state.update_data(q7=message.text)
    await message.answer("8) Последний вопрос:")
    await state.set_state(Survey.q8)

@router.message(Survey.q8)
async def survey_q8(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cursor.execute('''
        INSERT INTO survey (user_id, tg_id, name, age, subject, color, movie, q6, q7, q8)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['user_id'], data['tg_id'], data['name'], data['age'], data['subject'],
          data['color'], data['movie'], data['q6'], data['q7'], message.text))
    conn.commit()

    data = await state.get_data()

    result_text = (
        f"📊 *Ваши ответы:*\n"
        f"1️⃣ Имя: {data['name']}\n"
        f"2️⃣ Возраст: {data['age']}\n"
        f"3️⃣ Любимый предмет: {data['subject']}\n"
        f"4️⃣ Любимый цвет: {data['color']}\n"
        f"5️⃣ Любимый фильм: {data['movie']}\n"
        f"6️⃣ {data['q6']}\n"
        f"7️⃣ {data['q7']}\n"
        f"8️⃣ {message.text}"
    )

    await message.answer(result_text, parse_mode="Markdown")
    await state.clear()

@router.message()
async def menu_handler(message: types.Message):
    text = message.text.lower()
    if text == "шутка":
        await message.answer("Выберите категорию шуток:", reply_markup=joke_menu())
    elif text == "погода":
        weather = await fetch_weather()
        await message.answer(weather)
    elif text == "курс валют":
        currency_data = await fetch_currency()
        if currency_data.strip():
            await message.answer(currency_data)
    elif text == "список фильмов":
        movies = await fetch_movies()
        await message.answer(movies)
    elif text == "опрос":
        await message.answer("Начнем опрос! Как вас зовут?")
    elif text == "картинка":
        await message.answer("Выберите категорию изображения:", reply_markup=image_menu())

@router.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    data = callback.data

    if data.startswith("joke_"):
        category = data.split("_")[1]
        joke = await fetch_joke(category)
        await callback.message.answer(joke)
    elif data.startswith("image_"):
        category = data.split("_")[1]
        images = await get_random_images(category)

        if images:
            img_path = random.choice(images)  # Берём 1 случайную картинку
            photo = FSInputFile(img_path)
            await bot.send_photo(callback.message.chat.id, photo)
        else:
            await callback.message.answer("Ошибка: нет изображений в папке.")

        await callback.answer()

    elif data.startswith("weather_"):
        day = int(data.split("_")[1])
        weather_data = await fetch_weather()
        await callback.message.answer(weather_data)
        await callback.answer()

    await callback.answer()

async def get_random_images(category: str):
    folder_path = f"images/{category}/"
    images = [img for img in os.listdir(folder_path) if img.endswith((".jpg", ".png"))]
    random_images = random.sample(images, min(1, len(images)))
    return [folder_path + img for img in random_images]

dp.include_router(router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

