import sqlite3
from datetime import datetime, timedelta

# Создаем подключение к базе данных
def create_connection():
    conn = sqlite3.connect('database.db')
    return conn

# Создаем необходимые таблицы в базе данных
def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS services (
        service_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS timeslots (
        timeslot_id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_time TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        service_id INTEGER,
        timeslot_id INTEGER,
        FOREIGN KEY(service_id) REFERENCES services(service_id),
        FOREIGN KEY(timeslot_id) REFERENCES timeslots(timeslot_id)
    )
    ''')

    conn.commit()
    conn.close()

# Добавление нового пользователя
def add_user(user_id, name, phone):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (user_id, name, phone) VALUES (?, ?, ?)', (user_id, name, phone))
    conn.commit()
    conn.close()

# Получение пользователя по ID
def get_user_by_id(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Получение списка всех услуг
def get_services():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT service_id, name, price FROM services')
    services = cursor.fetchall()
    conn.close()
    return services

# Добавление новой услуги
def create_service(service_name, price):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO services (name, price) VALUES (?, ?)', (service_name, price))
    conn.commit()
    conn.close()

# Добавление нового временного слота
def create_timeslot(datetime_str):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO timeslots (date_time) VALUES (?)', (datetime_str,))
    conn.commit()
    conn.close()

# Получение доступных дат
def get_available_dates():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT date(date_time) FROM timeslots WHERE date_time > ?', (datetime.now().strftime('%Y-%m-%d'),))
    dates = cursor.fetchall()
    conn.close()
    return [date[0] for date in dates]

# Получение доступных временных слотов для конкретной даты
def get_available_times_for_date(selected_date):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT timeslot_id, time(date_time) FROM timeslots WHERE date(date_time) = ?', (selected_date,))
    timeslots = cursor.fetchall()
    conn.close()
    return timeslots

# Добавление временных слотов на месяц вперед
def create_month_timeslots(time_range):
    conn = create_connection()
    cursor = conn.cursor()

    start_time_str, end_time_str = time_range.split('-')
    start_time = datetime.strptime(start_time_str.strip(), '%H:%M').time()
    end_time = datetime.strptime(end_time_str.strip(), '%H:%M').time()

    current_date = datetime.now().date()
    end_date = current_date + timedelta(days=30)  # Слоты на 30 дней вперед

    while current_date <= end_date:
        current_datetime = datetime.combine(current_date, start_time)
        while current_datetime.time() <= end_time:
            cursor.execute('INSERT INTO timeslots (date_time) VALUES (?)', (current_datetime.strftime('%Y-%m-%d %H:%M'),))
            current_datetime += timedelta(minutes=60)  # Интервал 1 час
        current_date += timedelta(days=1)

    conn.commit()
    conn.close()

# Получение всех бронирований пользователя
def get_user_bookings(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT bookings.booking_id, services.name, timeslots.date_time 
    FROM bookings 
    JOIN services ON bookings.service_id = services.service_id 
    JOIN timeslots ON bookings.timeslot_id = timeslots.timeslot_id 
    WHERE bookings.user_id = ?
    ''', (user_id,))
    bookings = cursor.fetchall()
    conn.close()
    return bookings

# Создание нового бронирования
def create_booking(user_id, service_id, timeslot_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO bookings (user_id, service_id, timeslot_id) VALUES (?, ?, ?)', (user_id, service_id, timeslot_id))
    conn.commit()
    conn.close()

# Удаление бронирования
def delete_booking(booking_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM bookings WHERE booking_id = ?', (booking_id,))
    conn.commit()
    conn.close()
