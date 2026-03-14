import asyncio
import asyncpg
import datetime
from config import DATABASE_URL

async def main():
    conn = await asyncpg.connect(DATABASE_URL)
    rows = await conn.fetch("SELECT date, time, status FROM appointments WHERE date >= CURRENT_DATE AND status = 'free' ORDER BY date, time LIMIT 10")
    for r in rows:
        print(f"{r['date']} {r['time']} {type(r['time'])}")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
