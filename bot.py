import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import BOT_TOKEN, DATABASE_URL
from database import create_pool, init_db

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set in environment variables!")
        return
        
    logger.info("Starting bot...")
    
    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Подключение к БД, если есть URL
    pool = None
    if DATABASE_URL:
        pool = await create_pool(DATABASE_URL)
        await init_db(pool)
        dp['db_pool'] = pool
    else:
        logger.warning("DATABASE_URL is not set. Database not initialized. Working in local mode for now.")

    # Установка команд бота (меню)
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
    ])

    # Запуск polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
