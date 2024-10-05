from aiogram import Bot, Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor

from config import API_TOKEN
from admin_handlers import register_admin_handlers
from client_handlers import register_client_handlers
from database import setup_db

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Инициализация БД
setup_db()

# Регистрация хендлеров
register_admin_handlers(dp)
register_client_handlers(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
