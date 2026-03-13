import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import BOT_TOKEN, DATABASE_URL, YEREVAN_TZ
from database import create_pool, init_db
from datetime import datetime, timedelta

from handlers.admin import admin_router
from handlers.client import client_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def clean_old_records(pool):
    """Фоновая задача: раз в час проверяет и удаляет старые записи из БД"""
    while True:
        try:
            now_dt = datetime.now(YEREVAN_TZ)
            today = now_dt.date()
            now_time = now_dt.time()
            
            async with pool.acquire() as conn:
                # Удаляем все записи, у которых дата меньше сегодня, 
                # ИЛИ дата сегодня, но время уже прошло
                deleted = await conn.execute('''
                    DELETE FROM appointments 
                    WHERE date < $1 OR (date = $1 AND time < $2)
                ''', today, now_time)
                
                # Извлекаем количество удаленных строк из ответа вроде "DELETE 5"
                count = int(deleted.split()[-1]) if deleted.startswith("DELETE") else 0
                if count > 0:
                    logger.info(f"Очистка БД: удалено {count} устаревших слотов.")
        except Exception as e:
            logger.error(f"Ошибка при очистке БД: {e}")
            
        # Ждем 1 час перед следующей проверкой
        await asyncio.sleep(3600)

from datetime import time

async def auto_generate_schedule(pool):
    """Каждый день генерирует расписание на 14 дней вперед с 10:00 до 21:00."""
    while True:
        try:
            today = datetime.now(YEREVAN_TZ).date()
            
            async with pool.acquire() as conn:
                for i in range(3):
                    target_date = today + timedelta(days=i)
                    
                    # Если на этот день вообще ничего нет (ручных или забронированных слотов)
                    existing = await conn.fetchval('SELECT COUNT(*) FROM appointments WHERE date = $1', target_date)
                    if existing == 0:
                        current_dt = datetime.combine(target_date, time(10, 0))
                        end_dt = datetime.combine(target_date, time(21, 0))
                        
                        while current_dt <= end_dt:
                            await conn.execute('''
                                INSERT INTO appointments (date, time, status) 
                                VALUES ($1, $2, 'free') 
                                ON CONFLICT (date, time) DO NOTHING
                            ''', target_date, current_dt.time())
                            current_dt += timedelta(minutes=30)
                            
            logger.info("Авто-генерация расписания проверена/обновлена.")
        except Exception as e:
            logger.error(f"Ошибка при авто-генерации: {e}")
            
        # Ждем 6 часов до следующей проверки (чтобы точно не пропустить новый день)
        await asyncio.sleep(21600)

async def health_check(request):
    return web.Response(text="Bot is running!")

async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set in environment variables!")
        return
        
    logger.info("Starting bot...")
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    dp.include_router(admin_router)
    dp.include_router(client_router)

    if DATABASE_URL:
        pool = await create_pool(DATABASE_URL)
        await init_db(pool)
        dp.workflow_data.update({'db_pool': pool})
    else:
        logger.error("DATABASE_URL is not set!")
        return

    await bot.set_my_commands([
        BotCommand(command="start", description="Записаться к парикмахеру"),
        BotCommand(command="my_cancel", description="Отменить мою запись"),
    ])

    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем фоновую задачу очистки базы данных
    asyncio.create_task(clean_old_records(pool))
    
    # Запускаем авто-генератор расписания 
    asyncio.create_task(auto_generate_schedule(pool))
    
    # Запускаем веб-сервер для Render, чтобы он не убил проект
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Dummy web server started on port {port}")

    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
