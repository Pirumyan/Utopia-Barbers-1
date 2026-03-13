from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime, timedelta, date, time
import asyncpg
from config import ADMIN_IDS, YEREVAN_TZ

admin_router = Router()

def is_admin(message: Message) -> bool:
    return message.from_user.id in ADMIN_IDS

def get_yerevan_date() -> date:
    return datetime.now(YEREVAN_TZ).date()

@admin_router.message(Command("startday"))
async def cmd_startday(message: Message, db_pool: asyncpg.Pool):
    if not is_admin(message):
        await message.answer("У вас нет доступа к этой команде.")
        return

    # Форматы: /startday HH:MM HH:MM или /startday DD.MM HH:MM HH:MM
    args = message.text.split()[1:]
    
    if len(args) == 2:
        # Без даты, сегодня
        target_date = get_yerevan_date()
        start_str, end_str = args
    elif len(args) == 3:
        # С датой
        datestr, start_str, end_str = args
        try:
            day, month = map(int, datestr.split('.'))
            target_date = date(get_yerevan_date().year, month, day)
        except ValueError:
            await message.answer("Ошибка формата даты. Используйте DD.MM, например: 14.03")
            return
    else:
        await message.answer("Формат:\n/startday HH:MM HH:MM (на сегодня)\nили\n/startday DD.MM HH:MM HH:MM (на конкретный день)")
        return

    try:
        sh, sm = map(int, start_str.split(':'))
        eh, em = map(int, end_str.split(':'))
    except ValueError:
        # если пользователь передал просто "10 17"
        try:
            sh = int(start_str)
            sm = 0
            eh = int(end_str)
            em = 0
        except ValueError:
            await message.answer("Формат времени HH:MM, например: 10:45 17:35")
            return

    start_time = time(sh, sm)
    end_time = time(eh, em)

    # Генерируем слоты каждые 30 минут
    slots_created = 0
    current_dt = datetime.combine(target_date, start_time)
    end_dt = datetime.combine(target_date, end_time)

    async with db_pool.acquire() as conn:
        # Удаляем старые свободные слоты на эту дату, чтобы можно было перезаписать расписание
        await conn.execute("DELETE FROM appointments WHERE date = $1 AND status = 'free'", target_date)
        
        while current_dt < end_dt:
            slot_time = current_dt.time()
            try:
                await conn.execute('''
                    INSERT INTO appointments (date, time, status) 
                    VALUES ($1, $2, 'free') 
                    ON CONFLICT (date, time) DO NOTHING
                ''', target_date, slot_time)
                slots_created += 1
            except Exception:
                pass
            current_dt += timedelta(minutes=30)

    await message.answer(f"Рабочий день на {target_date.strftime('%d.%m.%Y')} создан с {start_time.strftime('%H:%M')} до {end_time.strftime('%H:%M')}.\nСоздано слотов: {slots_created}.")

@admin_router.message(Command("busy"))
async def cmd_busy(message: Message, db_pool: asyncpg.Pool):
    if not is_admin(message):
        return

    args = message.text.split()
    if len(args) != 2:
        await message.answer("Формат: /busy HH:MM")
        return

    try:
        hour, minute = map(int, args[1].split(':'))
        busy_time = time(hour, minute)
    except ValueError:
        await message.answer("Неверный формат времени.")
        return

    target_date = get_yerevan_date()

    async with db_pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO appointments (date, time, status) 
            VALUES ($1, $2, 'busy')
            ON CONFLICT (date, time) DO UPDATE SET status = 'busy', user_id = NULL
        ''', target_date, busy_time)

    await message.answer(f"Время {busy_time.strftime('%H:%M')} отмечено как занятое на сегодня.")

@admin_router.message(Command("cancel"))
async def cmd_cancel_admin(message: Message, db_pool: asyncpg.Pool, bot):
    if not is_admin(message):
        return

    args = message.text.split()
    if len(args) != 2:
        await message.answer("Формат: /cancel HH:MM")
        return

    try:
        hour, minute = map(int, args[1].split(':'))
        cancel_time = time(hour, minute)
    except ValueError:
        await message.answer("Неверный формат времени.")
        return

    target_date = get_yerevan_date()

    async with db_pool.acquire() as conn:
        appointment = await conn.fetchrow('''
            SELECT a.id, a.user_id, u.telegram_id 
            FROM appointments a 
            JOIN users u ON a.user_id = u.id 
            WHERE a.date = $1 AND a.time = $2 AND a.status = 'booked'
        ''', target_date, cancel_time)

        if not appointment:
            await message.answer("На это время нет записей.")
            return

        await conn.execute('''
            UPDATE appointments SET status = 'free', user_id = NULL 
            WHERE id = $1
        ''', appointment['id'])

        await message.answer(f"Запись на {cancel_time.strftime('%H:%M')} отменена. Слот снова свободен.")

        try:
            await bot.send_message(
                appointment['telegram_id'], 
                "К сожалению запись отменена. Пожалуйста выберите другое время."
            )
        except Exception:
            pass

@admin_router.message(Command("dayoff"))
async def cmd_dayoff(message: Message, db_pool: asyncpg.Pool):
    if not is_admin(message):
        return

    args = message.text.split()
    if len(args) != 2:
        await message.answer("Формат: /dayoff DD.MM")
        return

    try:
        day, month = map(int, args[1].split('.'))
        target_date = date(get_yerevan_date().year, month, day)
    except ValueError:
        await message.answer("Ошибка формата даты. Используйте DD.MM, например: 14.03")
        return

    async with db_pool.acquire() as conn:
        deleted = await conn.execute("DELETE FROM appointments WHERE date = $1 AND status = 'free'", target_date)
        count = int(deleted.split()[-1]) if deleted.startswith("DELETE") else 0

    await message.answer(f"Все свободные слоты ({count} шт.) на {target_date.strftime('%d.%m.%Y')} удалены (назначен Выходной).")

@admin_router.message(Command("schedule"))
async def cmd_schedule(message: Message, db_pool: asyncpg.Pool):
    if not is_admin(message):
        return

    today = get_yerevan_date()
    end_date = today + timedelta(days=2) # 3 дня: сегодня, завтра, послезавтра

    async with db_pool.acquire() as conn:
        appointments = await conn.fetch('''
            SELECT a.date, a.time, u.name, u.surname, u.phone, u.telegram_id
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE a.status = 'booked' AND a.date >= $1 AND a.date <= $2
            ORDER BY a.date, a.time
        ''', today, end_date)

    if not appointments:
        await message.answer("На ближайшие 3 дня записей нет.")
        return

    text = "🗓 <b>Расписание на ближайшие 3 дня:</b>\n"
    current_date = None
    
    for app in appointments:
        if app['date'] != current_date:
            current_date = app['date']
            text += f"\n📅 <b>{current_date.strftime('%d.%m.%Y')}</b>\n"
        
        username = f'<a href="tg://user?id={app["telegram_id"]}">{app["name"]} {app["surname"]}</a>'
        text += f"⏰ {app['time'].strftime('%H:%M')} — {username} ({app['phone']})\n"

    # Если текст слишком длинный, Telegram может ругаться (лимит 4096 символов).
    # Но для 3 дней записей это вряд ли произойдет.
    await message.answer(text, parse_mode="HTML")
