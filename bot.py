import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import BOT_TOKEN, DATABASE_URL
from database import create_pool, init_db

from handlers.admin import admin_router
from handlers.client import client_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Middleware для передачи db_pool в обработчики
class DbPoolMiddleware:
    def __init__(self, pool):
        self.pool = pool

    async def __call__(self, handler, event, data):
        data['db_pool'] = self.pool
        return await handler(event, data)

async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set in environment variables!")
        return
        
    logger.info("Starting bot...")
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Подключаем роутеры
    dp.include_router(admin_router)
    dp.include_router(client_router)

    if DATABASE_URL:
        pool = await create_pool(DATABASE_URL)
        await init_db(pool)
        
        # Передаем db_pool как глобальную зависимость (для aiogram 3)
        dp.workflow_data.update({'db_pool': pool})
    else:
        logger.error("DATABASE_URL is not set!")
        return

    # Меню команд
    await bot.set_my_commands([
        BotCommand(command="start", description="Записаться к парикмахеру"),
        BotCommand(command="my_cancel", description="Отменить мою запись"),
    ])

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
