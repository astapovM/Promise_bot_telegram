import asyncio
import datetime
import logging
import random
import re

import aioschedule
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor
from aiogram_calendar import simple_cal_callback, SimpleCalendar

import buttons
import db_admin
import remember_list
from config import token
from mail_sendler import send_email

email = "me@host.com"

pattern = r"^[-\w\.]+@([-\w]+\.)+[-\w]{2,4}$"

logging.basicConfig(filename='log.txt', filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S', encoding='UTF-8', level=logging.DEBUG)
logging.info("Log started")

bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())
db_admin.sql_start()

now = datetime.datetime.now()


class Promises(StatesGroup):
    promis_text = State()
    promis_date = State()
    promis_email = State()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    if db_admin.check_user(message.from_user.id) != None:
        await message.answer("Опять ты ? \n"
                             "Нажми кнопку, чтобы узнать что ты обещал:  ", reply_markup=buttons.check_promise_button)

    else:
        await message.answer(f"Привет {message.from_user.full_name}.\n"
                             f"Я бот напоминалка.Оставь мне обещание,и я буду о нем напоминать",
                             reply_markup=buttons.promise_button)


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer("Оставь обещание и я буду о нем напоминать . Используй клавиатуру для выбора")


@dp.message_handler(text='Дать обещание')
async def promise(message: types.Message):
    await Promises.promis_text.set()
    await message.answer("Хорошо.Напиши что ты хочешь пообещать", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Promises.promis_text)
async def answer_text(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    async with state.proxy() as data:
        data["user_id"] = user_id
        data["user_name"] = user_name
        data["promise"] = message.text
        await message.delete()

    await state.reset_state(with_data=False)
    await message.answer("Хорошо.Теперь введи дату дедлайна", reply_markup=await SimpleCalendar().start_calendar())


@dp.callback_query_handler(simple_cal_callback.filter())
async def answer_date(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(call, callback_data)
    if selected:
        await Promises.promis_date.set()
        await state.update_data(deadline=f'{date.strftime("%Y.%m.%d")}')
        data = await state.get_data()
        await db_admin.sql_add(data)
        await state.finish()
        if db_admin.sql_deadline(call.from_user.id)[0] < now.strftime("%Y.%m.%d"):
            await bot.send_message(call.from_user.id, "Вы выбрали уже прошедшее время.Обещание не было создано")
            db_admin.sql_delete(call.from_user.id)
        else:
            await bot.send_message(call.from_user.id, f'Ты пообещал {data["promise"]} до {data["deadline"]}')
            await bot.send_message(call.from_user.id, "Но кому ты даешь это обещание ?",
                                   reply_markup=buttons.promise_email)


@dp.message_handler(text="Себе")
async def answer_sebe(message: types.Message):
    await message.answer("Ок.Буду переодически тебе напоминать об этом", reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Просто введи /start ,  для дальнейшего общения со мной")


@dp.message_handler(text="Другому человеку")
async def answer_another(message: types.Message):
    await message.answer("Тогда введите его email адрес", reply_markup=types.ReplyKeyboardRemove())
    await Promises.promis_email.set()


@dp.message_handler(state=Promises.promis_email)
async def answer_email(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text
        if "@" not in message.text:
            await message.answer("Введите адрес почты в верном формате (lohpidor@mail.ru)")
            await Promises.promis_email.set()
        else:
            await db_admin.sql_add_email(data, message.from_user.id)
            await state.finish()
            await message.delete()
            await message.answer(
                f"Почта записана.Если ты не выполнишь своё обещание до {db_admin.promise_check(message.from_user.id)[1]} человеку придет письмо"
                f" с рассказом о том, как ты его обманул и не выполнил обещанного.")
            await message.answer("Просто введи /start ,  для дальнейшего общения со мной")



@dp.message_handler(text="Проверить обещание")
async def check_promise(message: types.Message):
    db_admin.promise_check(message.from_user.id)
    await message.answer(
        f"Ты обещал {db_admin.check_promise(message.from_user.id)[0]} до {db_admin.promise_check(message.from_user.id)[1]}")
    await message.answer("Ты выполнил это обещание?", reply_markup=buttons.promise_answer_button)


@dp.message_handler(text="Выполнил")
async def answer_yes(message: types.Message):
    await message.answer("Значит можно удалять ?", reply_markup=buttons.delete_promise_button)
    db_admin.sql_delete(message.from_user.id)


@dp.message_handler(text="Удалить обещание")
async def delete_promise(message: types.Message):
    await message.answer("Обещание удалено."
                         "Можете оставлять новое.\n"
                         "Для этого снова запустите бота командой /start или с помощью menu",
                         reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(text="Еще нет")
async def answer_no(message: types.Message):
    await bot.send_photo(message.from_user.id, "https://raritem.ru/wp-content/uploads/2021/12/thing.jpg",
                         reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['sendall'])
async def sendall(message: types.Message):
    if message.from_user.id == 293427068:
        while True:
            text = random.choice(remember_list.spisok)
            users = db_admin.all_users()
            for user in users:
                await bot.send_message(user[0], text)
                print(f"Сообщение юзеру {user} доставлено")
            await asyncio.sleep(random.randint(120, 240))


@dp.message_handler(commands=['spam'])
async def spam(message):
    for deadline in db_admin.check_info():
        if deadline[1] <= now.strftime("%Y.%m.%d"):
            await bot.send_message(deadline[0],
                                   "Время вышло и ты не выполнил обещание.Отныне ты официально чорт.Поздравляем  🥳 🥳  🥳  ")

            for mail in db_admin.check_email():
                if mail[0] != None:
                    print(mail[0])
                    await send_email(f"{mail[0]}")
                    db_admin.sql_delete(deadline[0])

        else:
            text = random.choice(remember_list.spisok)
            await bot.send_message(deadline[0], text)
            print(f"Сообщение юзеру {deadline[0]} доставлено в {now.strftime('%H:%M  %d.%m.%Y')}!")


async def scheduler():
    aioschedule.every().day.at("12:35").do(spam, "message")
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(10)


async def on_startup(_):
    asyncio.create_task(scheduler())


@dp.message_handler(commands=['sendone'])
async def sendone(message: types.Message):
    if message.from_user.id == 293427068:
        text = ("Ну шо ты , маладой шершень.Не забыл еще что обещал?")
        user_volos = 161611465
        user_admin = 293427068
        user_star = 87241346
        user_vovan = 881052206
        user_vlad = 343308620
        await bot.send_photo(user_star, "https://memepedia.ru/wp-content/uploads/2017/07/1429875891_1642837939.png")
        print(f"Сообщение юзеру {user_star} доставлено в {now.strftime('%H:%M  %d.%m.%Y')}!")


@dp.message_handler()
async def command_not_found(message: types.Message):
    await message.delete()
    await message.answer(f"Команда {message.message_id} не найдена")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
