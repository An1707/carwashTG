from aiogram import types
from database import get_db_connection

# Добавление услуги (для админа)
async def add_service(message: types.Message):
    user_id = message.from_user.id
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT is_admin FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result and result[0]:  # Если админ
        try:
            data = message.text.split()
            service_name = data[1]
            price = float(data[2])
            cursor.execute("INSERT INTO services (service_name, price) VALUES (?, ?)", (service_name, price))
            conn.commit()
            await message.answer(f"Услуга '{service_name}' добавлена с ценой {price} руб.")
        except Exception as e:
            await message.answer("Ошибка при добавлении услуги. Используйте формат: /add_service [название] [цена]")
    else:
        await message.answer("У вас нет прав для выполнения этой команды.")
    conn.close()

# Добавление доступного времени (для админа)
async def add_time(message: types.Message):
    user_id = message.from_user.id
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT is_admin FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result and result[0]:  # Если админ
        try:
            data = message.text.split()
            date = data[1]
            time = data[2]
            cursor.execute("INSERT INTO available_times (date, time, is_available) VALUES (?, ?, 1)", 
                           (date, time))
            conn.commit()
            await message.answer(f"Время {date} {time} добавлено как доступное.")
        except Exception as e:
            await message.answer("Ошибка при добавлении времени. Используйте формат: /add_time [дата] [время]")
    else:
        await message.answer("У вас нет прав для выполнения этой команды.")
    conn.close()

# Регистрация хендлеров для админов
def register_admin_handlers(dp):
    dp.register_message_handler(add_service, commands=['add_service'])
    dp.register_message_handler(add_time, commands=['add_time'])
