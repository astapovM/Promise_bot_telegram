import random
import asyncio
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils import executor
from aiogram_calendar import simple_cal_callback, SimpleCalendar, dialog_cal_callback, DialogCalendar
import buttons
import db_admin
import remember_list
from config import token

bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())
db_admin.sql_start()


class Promises(StatesGroup):
    promis_text = State()
    promis_date = State()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    db_admin.check_user(message.from_user.id)
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

    await state.reset_state(with_data=False)
    await message.answer("Хорошо.Теперь введи дату дедлайна",reply_markup=await SimpleCalendar().start_calendar())

@dp.callback_query_handler(simple_cal_callback.filter())
async def answer_date(call: types.CallbackQuery,callback_data: dict, state: FSMContext):
    selected, date = await SimpleCalendar().process_selection(call, callback_data)
    if selected:
        await Promises.promis_date.set()
        await state.update_data(deadline=f'{date.strftime("%d.%m.%Y")}')
        data = await state.get_data()
        await db_admin.sql_add(data)
        await state.finish()
        await bot.send_message(call.from_user.id, f'Ты пообещал {data["promise"]} до {data["deadline"]}')
        await bot.send_message(call.from_user.id, "Буду переодически тебе напоминать об этом")
        while True:
            await asyncio.sleep(random.randint(120, 240))
            db_admin.check_user(message.from_user.id)
            if db_admin.check_user(call.from_user.id) != None:
                text = random.choice(remember_list.spisok)
                await bot.send_message(call.from_user.id, text)
                print(f"Сообщение юзеру {call.from_user.id} доставлено!")

            else:
                break














@dp.message_handler(text="Проверить обещание")
async def check_promise(message: types.Message):
    db_admin.promise_check(message.from_user.id)
    await message.answer(
        f"Ты обещал {db_admin.promise_check(message.from_user.id)[0]} до {db_admin.promise_check(message.from_user.id)[1]}")
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
    await bot.send_photo(message.from_user.id, "https://oir.mobi/uploads/posts/2019-12/1575947618_3-3.jpg",
                         reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['sendall'])
async def sendall(message: types.Message):
    if message.chat.type == "private":
        if message.from_user.id == 293427068:

            while True:

                text = random.choice(remember_list.spisok)
                users = db_admin.all_users()
                for user in users:
                    await bot.send_message(user[0], text)
                    print(f"Сообщение юзеру {user} доставлено")
                await asyncio.sleep(random.randint(120,240))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
