from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime, timedelta, date, time
import asyncpg
from config import ADMIN_IDS

admin_router = Router()

# Фильтр для проверки администратора
def is_admin(message: Message) -> bool:
    return message.from_user.id in ADMIN_IDS

@admin_router.message(Command("startday"))
async def cmd_startday(message: Message, db_pool: asyncpg.Pool):
    if not is_admin(message):
        await message.answer("У вас нет доступа к этой команде.")
        return

    # Парсим часы работы, например: /startday 10 17
    args = message.text.split()
    if len(args) != 3:
        await message.answer("Формат: /startday <начало> <конец>, например: /startday 10 17")
        return

    try:
        start_hour = int(args[1])
        end_hour = int(args[2])
    except ValueError:
        await message.answer("Часы должны быть числами.")
        return

    today = date.today()
    
    # Генерируем слоты каждые 30 минут
    slots_created = 0
    current_time = datetime.combine(today, time(start_hour, 0))
    end_time = datetime.combine(today, time(end_hour, 0))

    async with db_pool.acquire() as conn:
        while current_time < end_time:
            slot_time = current_time.time()
            
            # Пытаемся добавить свободный слот, если его еще нет
            try:
                await conn.execute('''
                    INSERT INTO appointments (date, time, status) 
                    VALUES ($1, $2, 'free') 
                    ON CONFLICT (date, time) DO NOTHING
                ''', today, slot_time)
                slots_created += 1
            except Exception as e:
                pass
                
            current_time += timedelta(minutes=30)

    await message.answer(f"Рабочий день на {today.strftime('%d.%m.%Y')} создан с {start_hour}:00 до {end_hour}:00.\nСоздано слотов: {slots_created}.")

@admin_router.message(Command("busy"))
async def cmd_busy(message: Message, db_pool: asyncpg.Pool):
    if not is_admin(message):
        await message.answer("У вас нет доступа к этой команде.")
        return

    # Парсим время: /busy 11:00
    args = message.text.split()
    if len(args) != 2:
        await message.answer("Формат: /busy HH:MM, например: /busy 11:00")
        return

    try:
        hour, minute = map(int, args[1].split(':'))
        busy_time = time(hour, minute)
    except ValueError:
        await message.answer("Неверный формат времени.")
        return

    today = date.today()

    async with db_pool.acquire() as conn:
        # Устанавливаем статус completed/busy или просто добавляем слот-заглушку
        res = await conn.execute('''
            INSERT INTO appointments (date, time, status) 
            VALUES ($1, $2, 'busy')
            ON CONFLICT (date, time) DO UPDATE SET status = 'busy', user_id = NULL
        ''', today, busy_time)

    await message.answer(f"Время {busy_time.strftime('%H:%M')} отмечено как занятое.")

@admin_router.message(Command("cancel"))
async def cmd_cancel_admin(message: Message, db_pool: asyncpg.Pool, bot):
    if not is_admin(message):
        await message.answer("У вас нет доступа к этой команде.")
        return

    args = message.text.split()
    if len(args) != 2:
        await message.answer("Формат: /cancel HH:MM, например: /cancel 15:00")
        return

    try:
        hour, minute = map(int, args[1].split(':'))
        cancel_time = time(hour, minute)
    except ValueError:
        await message.answer("Неверный формат времени.")
        return

    today = date.today()

    async with db_pool.acquire() as conn:
        # Ищем запись на это время
        appointment = await conn.fetchrow('''
            SELECT a.id, a.user_id, u.telegram_id 
            FROM appointments a 
            JOIN users u ON a.user_id = u.id 
            WHERE a.date = $1 AND a.time = $2 AND a.status = 'booked'
        ''', today, cancel_time)

        if not appointment:
            await message.answer("На это время нет записей.")
            return

        # Отменяем (освобождаем слот)
        await conn.execute('''
            UPDATE appointments SET status = 'free', user_id = NULL 
            WHERE id = $1
        ''', appointment['id'])

        await message.answer(f"Запись на {cancel_time.strftime('%H:%M')} отменена. Слот снова свободен.")

        # Уведомляем клиента
        try:
            await bot.send_message(
                appointment['telegram_id'], 
                "К сожалению запись отменена. Пожалуйста выберите другое время."
            )
        except Exception:
            pass # Пользователь мог заблокировать бота
