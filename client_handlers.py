from aiogram import types
from database import get_db_connection

# Вывод услуг для клиента
async def list_services(message: types.Message):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT service_name, price FROM services")
    services = cursor.fetchall()
    
    response = "Доступные услуги:\n"
    for service in services:
        response += f"{service[0]} - {service[1]} руб.\n"
    await message.answer(response)
    conn.close()

# Вывод доступного времени
async def list_available_times(message: types.Message):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT date, time FROM available_times WHERE is_available = 1")
    times = cursor.fetchall()

    if times:
        response = "Доступное время для записи:\n"
        for time in times:
            response += f"{time[0]} - {time[1]}\n"
    else:
        response = "Свободного времени нет."
    
    await message.answer(response)
    conn.close()

# Запись на услугу
async def book_service(message: types.Message):
    try:
        data = message.text.split()
        service_name = data[1]
        booking_date = data[2]
        booking_time = data[3]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT service_id FROM services WHERE service_name = ?", (service_name,))
        service = cursor.fetchone()

        if not service:
            await message.answer("Услуга не найдена.")
            return

        user_id = message.from_user.id
        service_id = service[0]

        cursor.execute("SELECT * FROM available_times WHERE date = ? AND time = ? AND is_available = 1", 
                       (booking_date, booking_time))
        time_slot = cursor.fetchone()

        if time_slot:
            cursor.execute("INSERT INTO bookings (user_id, service_id, date, time) VALUES (?, ?, ?, ?)", 
                           (user_id, service_id, booking_date, booking_time))
            cursor.execute("UPDATE available_times SET is_available = 0 WHERE date = ? AND time = ?", 
                           (booking_date, booking_time))
            conn.commit()
            await message.answer(f"Вы успешно записаны на {service_name} {booking_date} в {booking_time}")
        else:
            await message.answer("Это время недоступно для записи.")
        conn.close()
    except Exception as e:
        await message.answer("Ошибка при записи. Используйте формат: /book [услуга] [дата] [время]")

# Отмена записи
async def cancel_booking(message: types.Message):
    try:
        data = message.text.split()
        booking_id = int(data[1])

        conn = get_db_connection()
        cursor = conn.cursor()

        user_id = message.from_user.id
        cursor.execute("SELECT * FROM bookings WHERE booking_id = ? AND user_id = ?", (booking_id, user_id))
        booking = cursor.fetchone()

        if booking:
            cursor.execute("DELETE FROM bookings WHERE booking_id = ?", (booking_id,))
            cursor.execute("UPDATE available_times SET is_available = 1 WHERE date = ? AND time = ?", 
                           (booking[2], booking[3]))
            conn.commit()
            await message.answer("Ваша запись отменена.")
        else:
            await message.answer("Запись не найдена.")
        conn.close()
    except Exception as e:
        await message.answer("Ошибка при отмене записи. Используйте формат: /cancel_booking [ID записи]")

# Просмотр текущих записей
async def my_bookings(message: types.Message):
    user_id = message.from_user.id
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT services.service_name, bookings.date, bookings.time 
        FROM bookings 
        JOIN services ON bookings.service_id = services.service_id 
        WHERE bookings.user_id = ?
    """, (user_id,))
    bookings = cursor.fetchall()

    if bookings:
        response = "Ваши записи:\n"
        for booking in bookings:
            response += f"{booking[0]} - {booking[1]} {booking[2]}\n"
    else:
        response = "
