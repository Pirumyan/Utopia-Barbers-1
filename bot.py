import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import BOT_TOKEN, DATABASE_URL
from database import create_pool, init_db

from handlers.admin import admin_router
from handlers.client import client_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
