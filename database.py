import sqlite3

def setup_db():
    conn = sqlite3.connect('carwash.db')
    cursor = conn.cursor()
    
    # Создание таблиц
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        is_admin BOOLEAN
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (
        service_id INTEGER PRIMARY KEY,
        service_name TEXT,
        price REAL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id INTEGER PRIMARY KEY,
        user_id INTEGER,
        service_id INTEGER,
        date TEXT,
        time TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (service_id) REFERENCES services(service_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS available_times (
        time_id INTEGER PRIMARY KEY,
        date TEXT,
        time TEXT,
        is_available BOOLEAN
    );
    """)

    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect('carwash.db')
