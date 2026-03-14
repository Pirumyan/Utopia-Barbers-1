from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime, timedelta, date, time
import asyncpg
from config import ADMIN_IDS, YEREVAN_TZ
from database import get_user_lang
from locales import get_text

admin_router = Router()

def is_admin(message: Message) -> bool:
    return message.from_user.id in ADMIN_IDS

def get_yerevan_date() -> date:
    return datetime.now(YEREVAN_TZ).date()

@admin_router.message(Command("startday"))
async def cmd_startday(message: Message, db_pool: asyncpg.Pool):
    lang = await get_user_lang(message.from_user.id, db_pool)
    if not is_admin(message):
        await message.answer(get_text('admin_no_access', lang))
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
            await message.answer(get_text('admin_format_invalid_date', lang))
            return
    else:
        await message.answer(get_text('admin_format_startday', lang))
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
            await message.answer(get_text('admin_format_invalid_time', lang))
            return

    start_time = time(sh, sm)
    end_time = time(eh, em)

    # Генерируем слоты каждые 15 минут
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
            current_dt += timedelta(minutes=15)

    await message.answer(get_text('admin_startday_success', lang, date=target_date.strftime('%d.%m.%Y'), start=start_time.strftime('%H:%M'), end=end_time.strftime('%H:%M'), count=slots_created))

@admin_router.message(Command("busy"))
async def cmd_busy(message: Message, db_pool: asyncpg.Pool, bot: Bot):
    lang = await get_user_lang(message.from_user.id, db_pool)
    if not is_admin(message):
        await message.answer(get_text('admin_no_access', lang))
        return

    args = message.text.split()[1:]
    target_date = get_yerevan_date()
    start_time_str = None
    end_time_str = None
    
    if len(args) == 1:
        # Без даты, сегодня, 1 время: HH:MM
        start_time_str = args[0]
    elif len(args) == 2:
        if '.' in args[0]:
            # С датой, 1 время: DD.MM HH:MM
            datestr, start_time_str = args
            try:
                day, month = map(int, datestr.split('.'))
                target_date = date(get_yerevan_date().year, month, day)
            except ValueError:
                await message.answer(get_text('admin_format_invalid_date', lang))
                return
        else:
            # Сегодня, период: HH:MM HH:MM
            start_time_str, end_time_str = args
    elif len(args) == 3:
        # С датой, период: DD.MM HH:MM HH:MM
        datestr, start_time_str, end_time_str = args
        try:
            day, month = map(int, datestr.split('.'))
            target_date = date(get_yerevan_date().year, month, day)
        except ValueError:
            await message.answer(get_text('admin_format_invalid_date', lang))
            return
    else:
        await message.answer(get_text('admin_format_busy', lang))
        return

    try:
        sh, sm = map(int, start_time_str.split(':'))
        start_time = time(sh, sm)
    except ValueError:
        await message.answer(get_text('admin_format_invalid_time', lang))
        return

    end_time = None
    if end_time_str:
        try:
            eh, em = map(int, end_time_str.split(':'))
            end_time = time(eh, em)
        except ValueError:
            await message.answer(get_text('admin_format_invalid_time', lang))
            return

    async with db_pool.acquire() as conn:
        slots_created = 0
        current_dt = datetime.combine(target_date, start_time)
        
        target_times = []
        if not end_time:
            target_times.append(start_time)
        else:
            end_dt = datetime.combine(target_date, end_time)
            while current_dt < end_dt:
                target_times.append(current_dt.time())
                current_dt += timedelta(minutes=15)
                
        cancelled_users = {}
        
        for t in target_times:
            app = await conn.fetchrow('''
                SELECT a.user_id, u.telegram_id, u.name, u.lang as client_lang, a.service_type
                FROM appointments a JOIN users u ON a.user_id = u.id
                WHERE a.date = $1 AND a.time = $2 AND a.status = 'booked'
            ''', target_date, t)
            
            if app:
                user_id = app['user_id']
                tg_id = app['telegram_id']
                all_slots = await conn.fetch('''
                    SELECT time FROM appointments 
                    WHERE date = $1 AND user_id = $2 AND service_type = $3 ORDER BY time
                ''', target_date, user_id, app['service_type'])
                
                block = []
                current_block = []
                for row in all_slots:
                    slot_t = row['time']
                    if not current_block: current_block.append(slot_t)
                    else:
                        prev_t = current_block[-1]
                        if (datetime.combine(target_date, slot_t) - datetime.combine(target_date, prev_t)).total_seconds() == 900:
                            current_block.append(slot_t)
                        else:
                            if t in current_block: block = current_block
                            current_block = [slot_t]
                if t in current_block: block = current_block
                
                for bt in block:
                    await conn.execute('''
                        UPDATE appointments SET status = 'free', user_id = NULL, service_type = NULL
                        WHERE date = $1 AND time = $2
                    ''', target_date, bt)
                    
                if tg_id not in cancelled_users:
                    cancelled_users[tg_id] = {'lang': app['client_lang'] if app['client_lang'] else 'ru', 'time': block[0]}
                    
        for t in target_times:
            await conn.execute('''
                INSERT INTO appointments (date, time, status) 
                VALUES ($1, $2, 'busy')
                ON CONFLICT (date, time) DO UPDATE SET status = 'busy', user_id = NULL, service_type = NULL
            ''', target_date, t)
            slots_created += 1

    for tg_id, info in cancelled_users.items():
        try:
            await bot.send_message(tg_id, get_text('admin_cancel_notify_client', info['lang']))
        except Exception:
            pass

    if slots_created == 0 and end_time:
        await message.answer(get_text('admin_busy_fail', lang))
    elif slots_created == 1 and not end_time:
        await message.answer(get_text('admin_busy_success_single', lang, time=start_time.strftime('%H:%M'), date=target_date.strftime('%d.%m.%Y')))
    elif end_time:
        await message.answer(get_text('admin_busy_success_period', lang, start=start_time.strftime('%H:%M'), end=end_time.strftime('%H:%M'), count=slots_created, date=target_date.strftime('%d.%m.%Y')))

@admin_router.message(Command("cancel"))
async def cmd_cancel_admin(message: Message, db_pool: asyncpg.Pool, bot):
    lang = await get_user_lang(message.from_user.id, db_pool)
    if not is_admin(message):
        await message.answer(get_text('admin_no_access', lang))
        return

    args = message.text.split()[1:]
    
    if len(args) == 1:
        target_date = get_yerevan_date()
        time_str = args[0]
    elif len(args) == 2:
        datestr, time_str = args
        try:
            day, month = map(int, datestr.split('.'))
            target_date = date(get_yerevan_date().year, month, day)
        except ValueError:
            await message.answer(get_text('admin_format_invalid_date', lang))
            return
    else:
        await message.answer(get_text('admin_format_cancel', lang))
        return

    try:
        hour, minute = map(int, time_str.split(':'))
        cancel_time = time(hour, minute)
    except ValueError:
        await message.answer(get_text('admin_format_invalid_time', lang))
        return

    async with db_pool.acquire() as conn:
        appointment = await conn.fetchrow('''
            SELECT a.id, a.user_id, u.telegram_id, a.service_type, u.lang as client_lang 
            FROM appointments a 
            JOIN users u ON a.user_id = u.id 
            WHERE a.date = $1 AND a.time = $2 AND a.status = 'booked'
        ''', target_date, cancel_time)

        if not appointment:
            await message.answer(get_text('admin_cancel_not_found', lang, date=target_date.strftime('%d.%m'), time=cancel_time.strftime('%H:%M')))
            return

        user_id = appointment['user_id']
        st = appointment['service_type']
        
        all_user_slots = await conn.fetch('''
            SELECT time FROM appointments 
            WHERE date = $1 AND user_id = $2 AND service_type = $3 ORDER BY time
        ''', target_date, user_id, st)
        
        block = []
        current_block = []
        for row in all_user_slots:
            t = row['time']
            if not current_block: current_block.append(t)
            else:
                prev_t = current_block[-1]
                if (datetime.combine(target_date, t) - datetime.combine(target_date, prev_t)).total_seconds() == 900:
                    current_block.append(t)
                else:
                    if cancel_time in current_block: block = current_block
                    current_block = [t]
        if cancel_time in current_block: block = current_block
            
        if not block: block = [cancel_time]

        for t in block:
            await conn.execute('''
                UPDATE appointments SET status = 'free', user_id = NULL, service_type = NULL
                WHERE date = $1 AND time = $2 AND user_id = $3
            ''', target_date, t, user_id)

        await message.answer(get_text('admin_cancel_success', lang, date=target_date.strftime('%d.%m'), time=block[0].strftime('%H:%M')))

        try:
            client_lang = appointment['client_lang'] if appointment['client_lang'] else 'ru'
            await bot.send_message(
                appointment['telegram_id'], 
                get_text('admin_cancel_notify_client', client_lang)
            )
        except Exception:
            pass

@admin_router.message(Command("dayoff"))
async def cmd_dayoff(message: Message, db_pool: asyncpg.Pool, bot: Bot):
    lang = await get_user_lang(message.from_user.id, db_pool)
    if not is_admin(message):
        await message.answer(get_text('admin_no_access', lang))
        return

    args = message.text.split()
    if len(args) != 2:
        await message.answer(get_text('admin_format_dayoff', lang))
        return

    try:
        day, month = map(int, args[1].split('.'))
        target_date = date(get_yerevan_date().year, month, day)
    except ValueError:
        await message.answer(get_text('admin_format_invalid_date', lang))
        return

    async with db_pool.acquire() as conn:
        # Находим уникальных клиентов и время их первой записи в этот день
        booked_apps = await conn.fetch('''
            SELECT MIN(a.time) as start_time, u.telegram_id, u.name, u.lang as client_lang
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE a.date = $1 AND a.status = 'booked'
            GROUP BY u.telegram_id, u.name, u.lang
        ''', target_date)

        # Удаляем ВООБЩЕ ВСЕ слоты на эту дату (и свободные, и занятые)
        deleted = await conn.execute("DELETE FROM appointments WHERE date = $1", target_date)
        count = int(deleted.split()[-1]) if deleted.startswith("DELETE") else 0

    # Уведомляем клиентов об отмене (по 1 сообщению каждому)
    for app in booked_apps:
        try:
            client_lang = app['client_lang'] if app['client_lang'] else 'ru'
            await bot.send_message(
                app['telegram_id'],
                get_text('admin_dayoff_notify_client', client_lang, name=app['name'], date=target_date.strftime('%d.%m.%Y'), time=app['start_time'].strftime('%H:%M'))
            )
        except Exception:
            pass

    await message.answer(get_text('admin_dayoff_success', lang, count=count, date=target_date.strftime('%d.%m.%Y'), clients_count=len(booked_apps)))

@admin_router.message(Command("schedule", "shedule"))
async def cmd_schedule(message: Message, db_pool: asyncpg.Pool):
    lang = await get_user_lang(message.from_user.id, db_pool)
    if not is_admin(message):
        await message.answer(get_text('admin_no_access', lang))
        return

    today = get_yerevan_date()
    end_date = today + timedelta(days=2) # 3 дня: сегодня, завтра, послезавтра

    async with db_pool.acquire() as conn:
        appointments = await conn.fetch('''
            SELECT a.date, a.time, u.name, u.surname, u.phone, u.telegram_id, a.service_type
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE a.status = 'booked' AND a.date >= $1 AND a.date <= $2
            ORDER BY a.date, a.time
        ''', today, end_date)

    if not appointments:
        await message.answer(get_text('admin_schedule_empty', lang))
        return

    text = get_text('admin_schedule_title', lang)
    current_date = None
    last_print = None
    
    for app in appointments:
        if app['date'] != current_date:
            current_date = app['date']
            text += f"\n📅 <b>{current_date.strftime('%d.%m.%Y')}</b>\n"
        
        uid = f"{app['date']}_{app['telegram_id']}_{app['service_type']}"
        if uid != last_print:
            username = f'<a href="tg://user?id={app["telegram_id"]}">{app["name"]} {app["surname"]}</a>'
            svc_name = get_text(f"service_{app['service_type']}", lang)
            text += f"⏰ {app['time'].strftime('%H:%M')} — {username} ({app['phone']}) [{svc_name}]\n"
            last_print = uid

    await message.answer(text, parse_mode="HTML")

@admin_router.message(Command("workday"))
async def cmd_workday(message: Message, db_pool: asyncpg.Pool):
    lang = await get_user_lang(message.from_user.id, db_pool)
    if not is_admin(message):
        await message.answer(get_text('admin_no_access', lang))
        return

    args = message.text.split()
    if len(args) != 2:
        await message.answer(get_text('admin_format_workday', lang))
        return

    try:
        day, month = map(int, args[1].split('.'))
        target_date = date(get_yerevan_date().year, month, day)
    except ValueError:
        await message.answer(get_text('admin_format_invalid_date', lang))
        return

    start_time = time(10, 0)
    end_time = time(21, 0)
    slots_created = 0
    current_dt = datetime.combine(target_date, start_time)
    end_dt = datetime.combine(target_date, end_time)

    async with db_pool.acquire() as conn:
        # Сначала удаляем старые свободные слоты (если был dayoff, удалять нечего, но на всякий случай)
        await conn.execute("DELETE FROM appointments WHERE date = $1 AND status = 'free'", target_date)
        
        while current_dt <= end_dt:
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
            current_dt += timedelta(minutes=15)

    await message.answer(get_text('admin_workday_success', lang, date=target_date.strftime('%d.%m.%Y'), count=slots_created))
