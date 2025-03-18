from aiogram import Router, types
from aiogram.types import FSInputFile
from parsers import fetch_joke, fetch_weather
import random
import os

router = Router()

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
            img_path = random.choice(images)
            photo = FSInputFile(img_path)
            await callback.message.answer_photo(photo)
        else:
            await callback.message.answer("Ошибка: нет изображений в папке.")

    elif data.startswith("weather_"):
        day = int(data.split("_")[1])
        weather_data = await fetch_weather()
        await callback.message.answer(weather_data)

    await callback.answer()

async def get_random_images(category: str):
    folder_path = f"images/{category}/"
    images = [img for img in os.listdir(folder_path) if img.endswith((".jpg", ".png"))]
    return [os.path.join(folder_path, img) for img in images]
