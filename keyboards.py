from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Картинка"), KeyboardButton(text="Погода")],
        [KeyboardButton(text="Курс валют"), KeyboardButton(text="Список фильмов")],
        [KeyboardButton(text="Шутка"), KeyboardButton(text="Опрос")]
    ],
    resize_keyboard=True
)
def image_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Футбол", callback_data="image_football"),
            InlineKeyboardButton(text="Бокс", callback_data="image_boxing"),
            InlineKeyboardButton(text="Баскетбол", callback_data="image_basketball")
        ]
    ])

def joke_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Программисты", callback_data="joke_programming"),
            InlineKeyboardButton(text="Черный юмор", callback_data="joke_dark"),
            InlineKeyboardButton(text="Случайная", callback_data="joke_any")
        ]
    ])
