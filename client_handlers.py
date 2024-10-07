from aiogram.filters import Command, StateFilter
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from Database import get_services, create_booking, get_user_bookings, delete_booking, get_available_dates, get_available_times_for_date, add_user, get_user_by_id
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

# Определяем состояния через класс
class BookingStates(StatesGroup):
    register_name = State()
    register_phone = State()
    choose_service = State()
    choose_timeslot = State()

# Обработка команды /start
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user = get_user_by_id(message.from_user.id)
    if not user:
        await message.answer("Добро пожаловать! Пожалуйста, зарегистрируйтесь. Введите ваше имя:")
        await state.set_state(BookingStates.register_name)
    else:
        await show_client_menu(message)

# Процесс регистрации пользователя - ввод имени
@router.message(StateFilter(BookingStates.register_name))
async def process_register_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ваш номер телефона:")
    await state.set_state(BookingStates.register_phone)

# Процесс регистрации пользователя - ввод телефона
@router.message(StateFilter(BookingStates.register_phone))
async def process_register_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data['name']
    phone = message.text
    add_user(message.from_user.id, name, phone)
    await message.answer(f"Регистрация завершена! Добро пожаловать, {name}.")
    await show_client_menu(message)
    await state.clear()

# Меню клиента
async def show_client_menu(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Записаться на мойку", callback_data='book_service')],
        [InlineKeyboardButton(text="Просмотр услуг", callback_data='view_services')],  # Добавлена кнопка для просмотра услуг
        [InlineKeyboardButton(text="Отмена записи", callback_data='cancel_booking')],
        [InlineKeyboardButton(text="История записей", callback_data='booking_history')]
    ])
    await message.answer("Меню клиента:", reply_markup=keyboard)

# Обработка записи на услугу
@router.callback_query(lambda c: c.data == 'book_service')
async def handle_book_service(callback_query: types.CallbackQuery, state: FSMContext):
    services = get_services()
    if services:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{service[1]} - {service[2]} руб.", callback_data=f"service_{service[0]}")] for service in services
        ])
        await callback_query.message.answer("Выберите услугу:", reply_markup=keyboard)
        await state.set_state(BookingStates.choose_service)
    else:
        await callback_query.message.answer("Нет доступных услуг.")
    await callback_query.answer()

# Новый обработчик для просмотра услуг
@router.callback_query(lambda c: c.data == 'view_services')
async def handle_view_services(callback_query: types.CallbackQuery):
    services = get_services()
    if services:
        services_list = "\n".join([f"{service[1]} - {service[2]} руб." for service in services])
        await callback_query.message.answer(f"Доступные услуги:\n{services_list}")
    else:
        await callback_query.message.answer("Нет доступных услуг.")
    await callback_query.answer()

# Обработка выбора услуги
@router.callback_query(lambda c: c.data.startswith("service_"))
async def choose_service(callback_query: types.CallbackQuery, state: FSMContext):
    selected_service_id = int(callback_query.data.split("_")[1])
    await state.update_data(selected_service_id=selected_service_id)

    # Переходим к выбору даты
    dates = get_available_dates()
    if dates:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=date, callback_data=f"date_{date}")] for date in dates
        ])
        await callback_query.message.answer("Выберите дату:", reply_markup=keyboard)
        await state.set_state(BookingStates.choose_timeslot)
    else:
        await callback_query.message.answer("Нет доступных дат.")
    await callback_query.answer()

# Обработка выбора даты
@router.callback_query(lambda c: c.data.startswith("date_"))
async def choose_timeslot_for_date(callback_query: types.CallbackQuery, state: FSMContext):
    selected_date = callback_query.data.split("_")[1]
    await state.update_data(selected_date=selected_date)

    timeslots = get_available_times_for_date(selected_date)
    if timeslots:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=timeslot[1].split(':')[0] + ":" + timeslot[1].split(':')[1], callback_data=f"timeslot_{timeslot[0]}")] for timeslot in timeslots
        ])
        await callback_query.message.answer(f"Выберите время на {selected_date}:", reply_markup=keyboard)
        await state.set_state(BookingStates.choose_timeslot)
    else:
        await callback_query.message.answer(f"Нет доступных временных слотов на {selected_date}.")
    await callback_query.answer()

# Обработка выбора временного слота
@router.callback_query(lambda c: c.data.startswith("timeslot_"))
async def handle_timeslot_selection(callback_query: types.CallbackQuery, state: FSMContext):
    selected_timeslot_id = int(callback_query.data.split("_")[1])
    data = await state.get_data()
    selected_service_id = data.get('selected_service_id')
    user_id = callback_query.from_user.id

    # Создаем запись в базе данных
    create_booking(user_id, selected_service_id, selected_timeslot_id)
    await callback_query.message.answer("Запись успешно создана!")
    await state.clear()
    await callback_query.answer()

# История записей
@router.callback_query(lambda c: c.data == 'booking_history')
async def handle_booking_history(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    bookings = get_user_bookings(user_id)
    if bookings:
        history = "\n".join([f"{b[1]} - {b[2]}" for b in bookings])
        await callback_query.message.answer(f"История ваших записей:\n{history}")
    else:
        await callback_query.message.answer("У вас нет записей.")
    await callback_query.answer()

# Отмена записи
@router.callback_query(lambda c: c.data == 'cancel_booking')
async def handle_cancel_booking(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    bookings = get_user_bookings(user_id)
    if bookings:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{b[1]} - {b[2]}", callback_data=f"cancel_{b[0]}")] for b in bookings
        ])
        await callback_query.message.answer("Выберите запись для отмены:", reply_markup=keyboard)
    else:
        await callback_query.message.answer("У вас нет активных записей.")
    await callback_query.answer()

# Обработка отмены записи
@router.callback_query(lambda c: c.data.startswith("cancel_"))
async def process_cancel_booking(callback_query: types.CallbackQuery):
    booking_id = int(callback_query.data.split("_")[1])
    delete_booking(booking_id)
    await callback_query.message.answer("Запись успешно отменена.")
    await callback_query.answer()
