from aiogram import Router, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import sqlite3

# Создание роутера
router = Router()

# Определяем состояния
class Survey(StatesGroup):
    q1 = State()
    q2 = State()
    q3 = State()
    q4 = State()
    q5 = State()
    q6 = State()
    q7 = State()
    q8 = State()

# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect("survey.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS survey (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
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
    return conn

# Начало опроса
@router.message(lambda message: message.text.lower() == "опрос")
async def start_survey(message: types.Message, state: FSMContext):
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = message.from_user.id

    # Проверяем, проходил ли пользователь опрос
    cursor.execute("SELECT * FROM survey WHERE user_id = ?", (user_id,))
    existing_data = cursor.fetchone()
    if existing_data:
        await message.answer("📊 Вы уже проходили опрос! Вот ваши ответы:")
        result_text = (
            f"1️⃣ Имя: {existing_data[2]}\n"
            f"2️⃣ Возраст: {existing_data[3]}\n"
            f"3️⃣ Любимый предмет: {existing_data[4]}\n"
            f"4️⃣ Любимый цвет: {existing_data[5]}\n"
            f"5️⃣ Любимый фильм: {existing_data[6]}\n"
            f"6️⃣ {existing_data[7]}\n"
            f"7️⃣ {existing_data[8]}\n"
            f"8️⃣ {existing_data[9]}"
        )
        await message.answer(result_text)
        conn.close()
        return

    await message.answer("1) Как вас зовут?")
    await state.set_state(Survey.q1)
    conn.close()

# Обработчики вопросов
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
    await message.answer("6) Любимый вид спорта?:")
    await state.set_state(Survey.q6)

@router.message(Survey.q6)
async def survey_q6(message: types.Message, state: FSMContext):
    await state.update_data(q6=message.text)
    await message.answer("7) Любимое слово?:")
    await state.set_state(Survey.q7)

@router.message(Survey.q7)
async def survey_q7(message: types.Message, state: FSMContext):
    await state.update_data(q7=message.text)
    await message.answer("8) Ноут\комп\телефон:")
    await state.set_state(Survey.q8)

@router.message(Survey.q8)
async def survey_q8(message: types.Message, state: FSMContext):
    data = await state.get_data()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Сохраняем данные в базу
    cursor.execute('''
        INSERT INTO survey (user_id, name, age, subject, color, movie, q6, q7, q8)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        message.from_user.id,
        data.get('name'),
        data.get('age'),
        data.get('subject'),
        data.get('color'),
        data.get('movie'),
        data.get('q6'),
        data.get('q7'),
        message.text
    ))
    conn.commit()
    conn.close()

    # Формируем итоговые ответы
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
