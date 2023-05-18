import os

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())

class Booking(StatesGroup):
    number_of_rooms = State()
    budget = State()
    contact = State()
    telefon = State() 


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Крайоты", callback_data="Крайоты"))
    keyboard.add(types.InlineKeyboardButton(text="Хайфа", callback_data="Хайфа"))
    await bot.send_message(message.from_user.id,
        "Где вы ищете квартиру?",
        reply_markup=keyboard
    )
    

@dp.callback_query_handler(text=["Крайоты", "Хайфа"])
async def n_rooms(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="1-2", callback_data="1-2"))
    keyboard.add(types.InlineKeyboardButton(text="2-3", callback_data="2-3"))
    keyboard.add(types.InlineKeyboardButton(text="3-4", callback_data="3-4"))
    keyboard.add(types.InlineKeyboardButton(text="более 4", callback_data="более 4"))
    await state.set_state(Booking.budget)
    await bot.edit_message_text(
                           "Сколько комнат вам нужно?",
                           message.message.chat.id,
                           message.message.message_id,
                           reply_markup=keyboard)
    await state.update_data(place=message.data) 
    
    

@dp.callback_query_handler(text=["1-2", "2-3", "3-4", "более 4"], state=Booking.budget)
async def get_budget(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="2000-3000", callback_data="2000-3000"))
    keyboard.add(types.InlineKeyboardButton(text="3000-4000", callback_data="3000-4000"))
    keyboard.add(types.InlineKeyboardButton(text="4000-5500", callback_data="4000-5500"))
    keyboard.add(types.InlineKeyboardButton(text="Дорогой эксклюзив", callback_data="Дорогой эксклюзив"))
    await state.set_state(Booking.contact)
    await bot.edit_message_text(
                           "Какой у вас бюджет?",
                           message.message.chat.id,
                           message.message.message_id,
                           reply_markup=keyboard)
    await state.update_data(rooms=message.data)



@dp.callback_query_handler(text=["2000-3000", "3000-4000", "4000-5500", "Дорогой эксклюзив"], state=Booking.contact)
async def get_procedure(message: types.Message, state: FSMContext):
    await state.set_state(Booking.telefon)
    await bot.edit_message_text(
                           "Отправьте свой контактный номер (пример: 89999999) и мы с вами свяжемся!",
                           message.message.chat.id,
                           message.message.message_id)
    await state.update_data(price=message.data)

@dp.message_handler(regexp='^[0-9]+', state=Booking.telefon)
async def contact(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id,
        "Спасибо! Скоро мы позвоним!",
    )
    user_data = await state.get_data()
    await bot.send_message(470878772,
        f"Новая запись: место {user_data['place']}, колличество комнат {user_data['rooms']}, цена {user_data['price']}, телефон {message.text}"
    )
    await state.finish()

@dp.message_handler(commands="cancel", state="*")
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Действие отменено", reply_markup=types.ReplyKeyboardRemove())

if '__main__'==__name__:
    executor.start_polling(dp, skip_updates=True)
