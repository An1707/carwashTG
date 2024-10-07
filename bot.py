import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from Config import API_TOKEN
from Database import create_tables
from admin_handlers import router as admin_router
from client_handlers import router as client_router

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Создание таблиц
create_tables()

# Регистрация маршрутов
dp.include_router(admin_router)
dp.include_router(client_router)

# Запуск бота
if __name__ == '__main__':
    dp.run_polling(bot)
