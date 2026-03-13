import asyncpg
import logging

logger = logging.getLogger(__name__)

async def create_pool(db_url):
    return await asyncpg.create_pool(db_url)

async def init_db(pool):
    async with pool.acquire() as conn:
        # Создаем таблицу пользователей
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                name VARCHAR(255),
                surname VARCHAR(255),
                phone VARCHAR(20)
            )
        ''')
        
        # Создаем таблицу записей
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                date DATE NOT NULL,
                time TIME NOT NULL,
                status VARCHAR(20) DEFAULT 'booked',
                UNIQUE(date, time) -- Защита от двойной записи на уровне БД
            )
        ''')
        
        # Миграции (добавление новых колонок)
        try:
            await conn.execute('ALTER TABLE users ADD COLUMN lang VARCHAR(10) DEFAULT \'ru\'')
        except asyncpg.exceptions.DuplicateColumnError:
            pass

        try:
            await conn.execute('ALTER TABLE appointments ADD COLUMN service_type VARCHAR(50)')
        except asyncpg.exceptions.DuplicateColumnError:
            pass
        logger.info("Database initialized")
