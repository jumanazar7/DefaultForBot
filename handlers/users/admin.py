import asyncio

import pandas as pd
from aiogram import types
from aiogram.dispatcher import FSMContext

from data.config import ADMINS
from loader import dp, db, bot
from states.state import Reklama


yes_no = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Да')],
        [KeyboardButton(text='Нет')]
    ],
    resize_keyboard=True)

@dp.message_handler(text="/allusers", user_id=ADMINS)
async def get_all_users(message: types.Message):
    users = await db.select_all_users()
    tg_id = []
    name = []
    for user in users:
        tg_id.append(user[3])
        name.append(user[2])
    data = {
        "Telegram ID": tg_id,
        "Name": name
    }
    pd.options.display.max_rows = 10000
    df = pd.DataFrame(data)
    if len(df) > 50:
        for x in range(0, len(df), 50):
            await bot.send_message(message.chat.id, df[x:x + 50])
    else:
        await bot.send_message(message.chat.id, df)


@dp.message_handler(text="/reklama", user_id=ADMINS)
async def send_ad_to_all(message: types.Message):
    await message.answer("Введите текст рекламы")
    await Reklama.reklama.set()


@dp.message_handler(state=Reklama.reklama)
async def send_ad_to_all(message: types.Message, state: FSMContext):
    reklama_text = message.text
    await state.update_data(
        {"reklama": reklama_text}
    )

    await message.answer('Хотите добавить кнопки для перехода?',reply_markup=yes_no)
    await Reklama.reklama_2.set()

@dp.message_handler(state=Reklama.reklama_2)
async def rek(message:types.Message,state:FSMContext):
    answer = message.text
    if answer == 'Нет':
        data = await state.get_data()
        reklama = data.get("reklama")
        users = await db.select_all_users()
        for user in users:
            try:
                user_id = user['tg_id']
                await message.bot.send_message(chat_id=user_id, text=reklama)
                await asyncio.sleep(0.05)
                await state.finish()
            except aiogram.utils.exceptions.BotBlocked:
                pass
    elif answer == 'Да':
        await message.answer(f'Введите название для кнопки',reply_markup=ReplyKeyboardRemove())
        await Reklama.reklama_3.set()

@dp.message_handler(state=Reklama.reklama_3)
async def rek(message:types.Message,state:FSMContext):
    n = message.text
    await state.update_data(
        {"name": n}
    )
    await message.answer('Введите url ссылку для кнопки!')
    await Reklama.reklama_4.set()

@dp.message_handler(state=Reklama.reklama_4)
async def rek(message:types.Message,state:FSMContext):
    url = message.text
    await state.update_data(
        {"url": url}
    )
    await message.answer('Хотите добавить изображение?',reply_markup=yes_no)
    await Reklama.reklama_5.set()

@dp.message_handler(state=Reklama.reklama_5)
async def rek(message: types.Message, state: FSMContext):
    n = message.text
    if n == 'Нет':
        data = await state.get_data()
        url = data.get('url')
        reklama = data.get("reklama")
        name = data.get("name")
        users = await db.select_all_users()
        a = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f'{name}', url=url)]
            ]
        )
        for user in users:
            try:
                user_id = user['tg_id']
                await message.bot.send_message(chat_id=user_id, text=reklama, reply_markup=a)
                await asyncio.sleep(0.05)
                await state.finish()
            except aiogram.utils.exceptions.BotBlocked:
                pass
    elif 'Да':
        await message.answer('Отправьте изображение!')
        await Reklama.reklama_6.set()

@dp.message_handler(content_types=['photo'], state=Reklama.reklama_6)
async def foto(message: types.Message, state: FSMContext):
    photo = message.photo[-1].file_id
    data = await state.get_data()
    url = data.get('url')
    reklama = data.get("reklama")
    name = data.get("name")
    users = await db.select_all_users()
    a = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f'{name}', url=url)]
        ]
    )
    for user in users:
        try:
            user_id = user['tg_id']
            await message.bot.send_photo(chat_id=user_id, photo=photo, caption=reklama,  reply_markup=a)
            await asyncio.sleep(0.05)
            await state.finish()
        except aiogram.utils.exceptions.BotBlocked:
            pass


@dp.message_handler(text="/cleandb", user_id=ADMINS)
async def get_all_users(message: types.Message):
    db.delete_users()
    await message.answer("База данных очищена!")


@dp.message_handler(text="/cleanct", user_id=ADMINS)
async def get_all_cart(message: types.Message):
    db.delete_cart()
    await message.answer("База данных корзины очищена!")
