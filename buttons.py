from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b1 = KeyboardButton("Дать обещание")
b2 = KeyboardButton("Проверить обещание")
b3 = KeyboardButton("Удалить обещание")
b4 = KeyboardButton("Выполнил")
b5 = KeyboardButton("Еще нет")
b6 = KeyboardButton("Календарь")

start_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(b6)
promise_button=ReplyKeyboardMarkup(resize_keyboard=True).add(b1)
check_promise_button = ReplyKeyboardMarkup(resize_keyboard=True).add(b2)
delete_promise_button = ReplyKeyboardMarkup(resize_keyboard=True).add(b3)
promise_answer_button = ReplyKeyboardMarkup(resize_keyboard=True).add(b4,b5)
фывфывфывфыв