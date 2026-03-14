import asyncio
import asyncpg
import datetime
from config import DATABASE_URL, YEREVAN_TZ

async def main():
    conn = await asyncpg.connect(DATABASE_URL)
    
    today = datetime.datetime.now(YEREVAN_TZ).date()
    # Удаляем все свободные слоты начиная с сегодня
    await conn.execute("DELETE FROM appointments WHERE status = 'free' AND date >= $1", today)
    
    # Заново генерируем для сегодня, завтра и послезавтра
    for i in range(3):
        target_date = today + datetime.timedelta(days=i)
        start_time = datetime.time(10, 0)
        end_time = datetime.time(21, 0)
        
        current_dt = datetime.datetime.combine(target_date, start_time)
        end_dt = datetime.datetime.combine(target_date, end_time)
        
        slots_created = 0
        while current_dt <= end_dt:
            slot_time = current_dt.time()
            try:
                await conn.execute('''
                    INSERT INTO appointments (date, time, status) 
                    VALUES ($1, $2, 'free') 
                    ON CONFLICT (date, time) DO NOTHING
                ''', target_date, slot_time)
                slots_created += 1
            except Exception as e:
                pass
            current_dt += datetime.timedelta(minutes=15)
        print(f"Created {slots_created} slots for {target_date}")
            
    await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
