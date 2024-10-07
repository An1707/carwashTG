from aiogram import Router, types
from Config import ADMINS
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from Database import create_service, create_timeslot, create_month_timeslots, get_user_bookings
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

class AdminStates(StatesGroup):
    add_service_name = State()
    add_service_price = State()
    add_timeslot = State()
    add_month_timeslots = State()
    view_client_bookings = State()

# Команда /admin
@router.message(Command("admin"))
async def admin_menu(message: types.Message):
    if message.from_user.id in ADMINS:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Добавить услугу", callback_data='add_service')],
            [InlineKeyboardButton(text="Добавить время", callback_data='add_timeslot')],
            [InlineKeyboardButton(text="Добавить время на месяц", callback_data='add_month_timeslots')],
            [InlineKeyboardButton(text="Просмотр записей клиента", callback_data='view_client_bookings')]
        ])
        await message.answer("Админ меню:", reply_markup=keyboard)
    else:
        await message.answer("У вас нет прав доступа.")

# Добавление услуги
@router.callback_query(lambda c: c.data == 'add_service')
async def add_service(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите название услуги:")
    await state.set_state(AdminStates.add_service_name)
    await callback_query.answer()

@router.message(AdminStates.add_service_name)
async def process_service_name(message: types.Message, state: FSMContext):
    await state.update_data(service_name=message.text)
    await message.answer("Введите цену услуги:")
    await state.set_state(AdminStates.add_service_price)

@router.message(AdminStates.add_service_price)
async def process_service_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    service_name = data['service_name']
    price = float(message.text)
    create_service(service_name, price)
    await message.answer(f"Услуга '{service_name}' с ценой {price} добавлена.")
    await state.clear()

# Добавление временного слота
@router.callback_query(lambda c: c.data == 'add_timeslot')
async def add_timeslot(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Введите дату и время в формате YYYY-MM-DD HH:MM:")
    await callback_query.answer()

@router.message(AdminStates.add_timeslot)
async def process_timeslot(message: types.Message, state: FSMContext):
    create_timeslot(message.text)
    await message.answer(f"Временной слот {message.text} добавлен.")
    await state.clear()

# Добавление времени на месяц вперед
@router.callback_query(lambda c: c.data == 'add_month_timeslots')
async def add_month_timeslots(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите временной диапазон (например, 09:00-18:00):")
    await state.set_state(AdminStates.add_month_timeslots)
    await callback_query.answer()

@router.message(AdminStates.add_month_timeslots)
async def process_month_timeslots(message: types.Message, state: FSMContext):
    time_range = message.text
    try:
        create_month_timeslots(time_range)
        await message.answer(f"Временные слоты на месяц вперед добавлены.")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
    await state.clear()

# Просмотр записей клиента
@router.callback_query(lambda c: c.data == 'view_client_bookings')
async def view_client_bookings(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введите ID клиента для просмотра его записей:")
    await state.set_state(AdminStates.view_client_bookings)
    await callback_query.answer()

@router.message(AdminStates.view_client_bookings)
async def process_view_client_bookings(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text)
        bookings = get_user_bookings(user_id)
        if bookings:
            bookings_list = '\n'.join([f"{booking[1]} - {booking[2]}" for booking in bookings])
            await message.answer(f"Записи клиента {user_id}:\n{bookings_list}")
        else:
            await message.answer(f"У клиента {user_id} нет записей.")
    except ValueError:
        await message.answer("ID клиента должно быть числом. Попробуйте снова.")
    await state.clear()
