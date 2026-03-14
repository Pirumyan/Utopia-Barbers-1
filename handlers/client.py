from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import date, datetime, timedelta, time
import asyncpg
from config import ADMIN_IDS, YEREVAN_TZ
from database import get_user_lang
from locales import get_text

client_router = Router()

class BookingState(StatesGroup):
    waiting_for_service = State()
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_name = State()
    waiting_for_surname = State()
    waiting_for_phone = State()

def get_yerevan_now():
    return datetime.now(YEREVAN_TZ)

async def get_main_menu_keyboard(tg_id: int, db_pool: asyncpg.Pool, lang: str):
    now_dt = get_yerevan_now()
    today = now_dt.date()
    now_time = now_dt.time()
    
    async with db_pool.acquire() as conn:
        active_count = await conn.fetchval('''
            SELECT COUNT(DISTINCT date::text || service_type) FROM appointments
            WHERE user_id = (SELECT id FROM users WHERE telegram_id = $1)
            AND status = 'booked' AND (date > $2 OR (date = $2 AND time > $3))
        ''', tg_id, today, now_time)

    buttons = [[InlineKeyboardButton(text=get_text("btn_book", lang), callback_data="book_start")]]
    if active_count and active_count > 0:
        buttons.append([InlineKeyboardButton(text=get_text("btn_my_apps", lang), callback_data="my_appointments")])
        
    buttons.append([InlineKeyboardButton(text=get_text("btn_change_lang", lang), callback_data="change_lang")])
        
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@client_router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, db_pool: asyncpg.Pool):
    await state.clear()
    
    # Check if user has selected a language
    async with db_pool.acquire() as conn:
        lang = await conn.fetchval('SELECT lang FROM users WHERE telegram_id = $1', message.from_user.id)
        
    if not lang:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text="🇦🇲 Հայերեն", callback_data="lang_am")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
        ])
        await message.answer("Выберите язык / Ընտրեք լեզուն / Choose language:", reply_markup=keyboard)
        return

    keyboard = await get_main_menu_keyboard(message.from_user.id, db_pool, lang)
    await message.answer(get_text('main_menu', lang), reply_markup=keyboard)

@client_router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery, db_pool: asyncpg.Pool):
    lang = callback.data.split("_")[1]
    tg_id = callback.from_user.id
    
    async with db_pool.acquire() as conn:
        # Check if user exists
        user_exists = await conn.fetchval('SELECT id FROM users WHERE telegram_id = $1', tg_id)
        if user_exists:
            await conn.execute('UPDATE users SET lang = $1 WHERE telegram_id = $2', lang, tg_id)
        else:
            await conn.execute('INSERT INTO users (telegram_id, lang) VALUES ($1, $2) ON CONFLICT (telegram_id) DO UPDATE SET lang = EXCLUDED.lang', tg_id, lang)
            
    keyboard = await get_main_menu_keyboard(tg_id, db_pool, lang)
    await callback.message.edit_text(get_text('main_menu', lang), reply_markup=keyboard)

@client_router.callback_query(F.data == "change_lang")
async def process_change_lang(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="🇦🇲 Հայերեն", callback_data="lang_am")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
    ])
    await callback.message.edit_text("Выберите язык / Ընտրեք լեզուն / Choose language:", reply_markup=keyboard)

@client_router.callback_query(F.data == "back_to_main")
async def back_to_main_callback(callback: CallbackQuery, state: FSMContext, db_pool: asyncpg.Pool):
    await state.clear()
    lang = await get_user_lang(callback.from_user.id, db_pool)
    keyboard = await get_main_menu_keyboard(callback.from_user.id, db_pool, lang)
    await callback.message.edit_text(get_text('main_menu', lang), reply_markup=keyboard)

@client_router.callback_query(F.data == "my_appointments")
async def show_my_appointments(callback: CallbackQuery, db_pool: asyncpg.Pool):
    now_dt = get_yerevan_now()
    today = now_dt.date()
    now_time = now_dt.time()
    lang = await get_user_lang(callback.from_user.id, db_pool)

    async with db_pool.acquire() as conn:
        # Group apps by service and date (MIN time)
        apps = await conn.fetch('''
            SELECT MIN(a.id) as id, a.date, MIN(a.time) as start_time, a.service_type
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE u.telegram_id = $1 AND a.status = 'booked' AND (a.date > $2 OR (a.date = $2 AND a.time > $3))
            GROUP BY a.date, a.service_type
            ORDER BY a.date, start_time
        ''', callback.from_user.id, today, now_time)

    if not apps:
        await callback.answer(get_text('no_active_apps', lang), show_alert=True)
        return

    text = get_text('your_active_apps_title', lang)
    buttons = []
    
    for i, app in enumerate(apps, 1):
        app_date_str = app['date'].strftime('%d.%m.%Y')
        app_time_str = app['start_time'].strftime('%H:%M')
        svc_name = get_text(f'service_{app["service_type"]}', lang)
        
        text += f"{i}. {app_date_str} {app_time_str} - {svc_name}\n"
        
        app_dt = datetime.combine(app['date'], app['start_time'], tzinfo=YEREVAN_TZ)
        if app_dt - now_dt >= timedelta(hours=1):
            cancel_txt = get_text('btn_cancel_app', lang, time=app_time_str)
            buttons.append([InlineKeyboardButton(text=cancel_txt, callback_data=f"cancel_app_{app['id']}")])
            
    buttons.append([InlineKeyboardButton(text=get_text('btn_back', lang), callback_data="back_to_main")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")

@client_router.callback_query(F.data.startswith("cancel_app_"))
async def process_cancel_app(callback: CallbackQuery, db_pool: asyncpg.Pool, bot: Bot):
    app_id = int(callback.data.split("_")[2])
    now_dt = get_yerevan_now()
    lang = await get_user_lang(callback.from_user.id, db_pool)

    async with db_pool.acquire() as conn:
        appointment = await conn.fetchrow('''
            SELECT a.id, a.date, a.time, u.id as db_uid, u.name, u.surname, u.phone, a.status, a.service_type
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE a.id = $1 AND u.telegram_id = $2
        ''', app_id, callback.from_user.id)

        if not appointment or appointment['status'] != 'booked':
            await callback.answer(get_text('no_active_apps', lang), show_alert=True)
            return
            
        app_dt = datetime.combine(appointment['date'], appointment['time'], tzinfo=YEREVAN_TZ)
        
        if app_dt - now_dt < timedelta(hours=1):
            await callback.answer(get_text('cancel_too_late', lang), show_alert=True)
            return

        st = appointment['service_type']
        slots_to_free = 1
        if st == 'haircut': slots_to_free = 2
        elif st == 'combo': slots_to_free = 3
        
        u_id = appointment['db_uid']
        cdt = appointment['time']
        
        for _ in range(slots_to_free):
            await conn.execute('''
                UPDATE appointments SET status = 'free', user_id = NULL, service_type = NULL
                WHERE date = $1 AND time = $2 AND user_id = $3
            ''', appointment['date'], cdt, u_id)
            tmp = datetime.combine(appointment['date'], cdt) + timedelta(minutes=15)
            cdt = tmp.time()

    await callback.answer(get_text('cancel_success', lang), show_alert=True)
    
    for admin_id in ADMIN_IDS:
        try:
            admin_lang = await get_user_lang(admin_id, db_pool)
            svc_name_translated = get_text(f'service_{st}', admin_lang)
            admin_msg = get_text('admin_notify_cancel_app', admin_lang, name=f"{appointment['name']} {appointment['surname']}", service=svc_name_translated, phone=appointment['phone'], date=appointment['date'].strftime('%d.%m.%Y'), time=appointment['time'].strftime('%H:%M'))
            await bot.send_message(admin_id, admin_msg)
        except Exception:
            pass

    keyboard = await get_main_menu_keyboard(callback.from_user.id, db_pool, lang)
    await callback.message.edit_text(get_text('cancel_selected_menu', lang), reply_markup=keyboard)

@client_router.callback_query(F.data == "book_start")
async def start_booking(callback: CallbackQuery, db_pool: asyncpg.Pool, state: FSMContext):
    now_dt = get_yerevan_now()
    today = now_dt.date()
    now_time = now_dt.time()
    lang = await get_user_lang(callback.from_user.id, db_pool)
    
    async with db_pool.acquire() as conn:
        active_count = await conn.fetchval('''
            SELECT COUNT(DISTINCT date::text || service_type) FROM appointments
            WHERE user_id = (SELECT id FROM users WHERE telegram_id = $1)
            AND status = 'booked' AND (date > $2 OR (date = $2 AND time > $3))
        ''', callback.from_user.id, today, now_time)

        if active_count and active_count >= 2:
            await callback.answer(get_text('max_apps_reached', lang), show_alert=True)
            return

    buttons = [
        [InlineKeyboardButton(text=get_text('service_haircut', lang), callback_data="service_haircut")],
        [InlineKeyboardButton(text=get_text('service_beard', lang), callback_data="service_beard")],
        [InlineKeyboardButton(text=get_text('service_combo', lang), callback_data="service_combo")],
        [InlineKeyboardButton(text=get_text('btn_back', lang), callback_data="back_to_main")]
    ]
    
    await state.set_state(BookingState.waiting_for_service)
    await callback.message.edit_text(get_text('choose_service', lang), reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@client_router.callback_query(BookingState.waiting_for_service, F.data.startswith("service_"))
async def select_service(callback: CallbackQuery, state: FSMContext, db_pool: asyncpg.Pool):
    service = callback.data.split("_")[1]
    lang = await get_user_lang(callback.from_user.id, db_pool)
    
    await state.update_data(service=service)
    
    num_slots = 1
    if service == 'haircut': num_slots = 2
    elif service == 'combo': num_slots = 3
    
    now_dt = get_yerevan_now()
    today = now_dt.date()
    now_time = now_dt.time()
    
    async with db_pool.acquire() as conn:
        all_free = await conn.fetch('''
            SELECT date, time FROM appointments 
            WHERE status = 'free' AND (date > $1 OR (date = $1 AND time > $2))
            ORDER BY date, time
        ''', today, now_time)
        
    from collections import defaultdict
    free_by_date = defaultdict(list)
    for row in all_free:
        free_by_date[row['date']].append(row['time'])
        
    valid_dates = set()
    for d, times in free_by_date.items():
        if num_slots == 1:
            valid_dates.add(d)
        else:
            times.sort()
            for i in range(len(times) - num_slots + 1):
                is_consecutive = True
                curr_dt = datetime.combine(d, times[i])
                for j in range(1, num_slots):
                    next_dt = curr_dt + timedelta(minutes=15 * j)
                    if next_dt.time() != times[i+j]:
                        is_consecutive = False
                        break
                if is_consecutive:
                    valid_dates.add(d)
                    break
                    
    if not valid_dates:
        await callback.answer(get_text('no_free_slots', lang), show_alert=True)
        return
        
    sorted_dates = sorted(list(valid_dates))
    buttons = []
    
    for d in sorted_dates:
        buttons.append([InlineKeyboardButton(text=d.strftime('%d.%m.%Y'), callback_data=f"date_{d.isoformat()}")])
        
    buttons.append([InlineKeyboardButton(text=get_text('btn_back', lang), callback_data="book_start")])
    
    svc_name = get_text(f'service_{service}', lang)
    msg_text = get_text('choose_date', lang).format(service=svc_name)
    
    await state.set_state(BookingState.waiting_for_date)
    await callback.message.edit_text(msg_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

@client_router.callback_query(BookingState.waiting_for_date, F.data.startswith("date_"))
async def select_date(callback: CallbackQuery, state: FSMContext, db_pool: asyncpg.Pool):
    selected_date_str = callback.data.split("_")[1]
    selected_date = date.fromisoformat(selected_date_str)
    
    await state.update_data(selected_date=selected_date_str)
    
    user_data = await state.get_data()
    service = user_data.get('service', 'beard')
    lang = await get_user_lang(callback.from_user.id, db_pool)
    
    num_slots = 1
    if service == 'haircut': num_slots = 2
    elif service == 'combo': num_slots = 3
    
    now_dt = get_yerevan_now()
    today = now_dt.date()
    now_time = now_dt.time()
    
    async with db_pool.acquire() as conn:
        all_free = await conn.fetch('''
            SELECT time FROM appointments 
            WHERE date = $1 AND status = 'free' AND (date > $2 OR (date = $2 AND time > $3))
            ORDER BY time
        ''', selected_date, today, now_time)
        
    times = [r['time'] for r in all_free]
    valid_times = []
    
    if num_slots == 1:
        valid_times = times
    else:
        for i in range(len(times) - num_slots + 1):
            is_consecutive = True
            curr_dt = datetime.combine(selected_date, times[i])
            for j in range(1, num_slots):
                next_dt = curr_dt + timedelta(minutes=15 * j)
                if next_dt.time() != times[i+j]:
                    is_consecutive = False
                    break
            if is_consecutive:
                valid_times.append(times[i])

    if not valid_times:
        await callback.answer(get_text('date_full', lang), show_alert=True)
        return
        
    buttons = []
    row = []
    for t in valid_times:
        t_str = t.strftime('%H:%M')
        row.append(InlineKeyboardButton(text=t_str, callback_data=f"time_{t_str}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
            
    buttons.append([InlineKeyboardButton(text=get_text('btn_back', lang), callback_data=f"book_start")])
    
    msg_text = get_text('choose_time', lang).format(date=selected_date.strftime('%d.%m.%Y'))
    
    await state.set_state(BookingState.waiting_for_time)
    await callback.message.edit_text(msg_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@client_router.callback_query(BookingState.waiting_for_time, F.data.startswith("time_"))
async def select_time(callback: CallbackQuery, state: FSMContext, db_pool: asyncpg.Pool):
    selected_time_str = callback.data.split("_")[1]
    lang = await get_user_lang(callback.from_user.id, db_pool)
    
    user_data = await state.get_data()
    selected_date_str = user_data['selected_date']
    selected_date = date.fromisoformat(selected_date_str)
    
    hour, minute = map(int, selected_time_str.split(':'))
    selected_time_obj = time(hour, minute)

    now_dt = get_yerevan_now()
    today = now_dt.date()
    now_time = now_dt.time()

    if selected_date < today or (selected_date == today and selected_time_obj <= now_time):
        await callback.answer(get_text('time_passed', lang), show_alert=True)
        return

    service = user_data.get('service', 'beard')
    num_slots = 1
    if service == 'haircut': num_slots = 2
    elif service == 'combo': num_slots = 3
    
    async with db_pool.acquire() as conn:
        cdt = selected_time_obj
        for _ in range(num_slots):
            slot = await conn.fetchrow('''
                SELECT status FROM appointments WHERE date = $1 AND time = $2
            ''', selected_date, cdt)
            if not slot or slot['status'] != 'free':
                await callback.answer(get_text('time_taken', lang), show_alert=True)
                return
            tmp = datetime.combine(selected_date, cdt) + timedelta(minutes=15)
            cdt = tmp.time()

    await state.update_data(selected_time=selected_time_str)
    await state.set_state(BookingState.waiting_for_name)
    msg = get_text('ask_name', lang).format(date=selected_date.strftime('%d.%m'), time=selected_time_str)
    await callback.message.edit_text(msg)

@client_router.message(BookingState.waiting_for_name)
async def process_name(message: Message, state: FSMContext, db_pool: asyncpg.Pool):
    lang = await get_user_lang(message.from_user.id, db_pool)
    text = message.text.strip() if message.text else ""
    if len(text) < 2:
        await message.answer(get_text('err_name', lang))
        return
    await state.update_data(name=text)
    await state.set_state(BookingState.waiting_for_surname)
    await message.answer(get_text('ask_surname', lang))

@client_router.message(BookingState.waiting_for_surname)
async def process_surname(message: Message, state: FSMContext, db_pool: asyncpg.Pool):
    lang = await get_user_lang(message.from_user.id, db_pool)
    text = message.text.strip() if message.text else ""
    if len(text) < 2:
        await message.answer(get_text('err_surname', lang))
        return
    await state.update_data(surname=text)
    await state.set_state(BookingState.waiting_for_phone)
    await message.answer(get_text('ask_phone', lang))

@client_router.message(BookingState.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext, db_pool: asyncpg.Pool, bot: Bot):
    lang = await get_user_lang(message.from_user.id, db_pool)
    phone = message.text.strip() if message.text else ""
    if len(phone) < 5:
        await message.answer(get_text('err_phone', lang))
        return

    # Validate phone format: optional leading '+', then only digits. No letters allowed.
    check_phone = phone[1:] if phone.startswith('+') else phone
    if not check_phone.isdigit():
        await message.answer(get_text('err_phone_invalid', lang))
        return

    user_data = await state.get_data()
    name = user_data['name']
    surname = user_data['surname']
    selected_time_str = user_data['selected_time']
    hour, minute = map(int, selected_time_str.split(':'))
    selected_time_obj = time(hour, minute)
    selected_date = date.fromisoformat(user_data['selected_date'])
    service = user_data.get('service', 'beard')
    
    num_slots = 1
    if service == 'haircut': num_slots = 2
    elif service == 'combo': num_slots = 3

    tg_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else f'<a href="tg://user?id={tg_id}">Клиент</a>'

    async with db_pool.acquire() as conn:
        async with conn.transaction():
            # Check one more time before final commit with FOR UPDATE lock
            cdt = selected_time_obj
            for _ in range(num_slots):
                slot = await conn.fetchrow('SELECT status FROM appointments WHERE date = $1 AND time = $2 FOR UPDATE', selected_date, cdt)
                if not slot or slot['status'] != 'free':
                    await message.answer(get_text('time_taken', lang))
                await state.clear()
                kbd = await get_main_menu_keyboard(tg_id, db_pool, lang)
                await message.answer(get_text('main_menu', lang), reply_markup=kbd)
                return
            tmp = datetime.combine(selected_date, cdt) + timedelta(minutes=15)
            cdt = tmp.time()
            
        # Register user
        user_id = await conn.fetchval('''
            INSERT INTO users (telegram_id, name, surname, phone, lang)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (telegram_id) DO UPDATE 
            SET name = EXCLUDED.name, surname = EXCLUDED.surname, phone = EXCLUDED.phone
            RETURNING id
        ''', tg_id, name, surname, phone, lang)

        # Update slots
        cdt = selected_time_obj
        for _ in range(num_slots):
            await conn.execute('''
                UPDATE appointments SET status = 'booked', user_id = $1, service_type = $2
                WHERE date = $3 AND time = $4
            ''', user_id, service, selected_date, cdt)
            tmp = datetime.combine(selected_date, cdt) + timedelta(minutes=15)
            cdt = tmp.time()

    await state.clear()
    
    svc_name = get_text(f'service_{service}', lang)
    msg_txt = get_text('booking_success', lang).format(
        service=svc_name,
        date=selected_date.strftime('%d.%m.%Y'),
        time=selected_time_str
    )
    
    keyboard = await get_main_menu_keyboard(tg_id, db_pool, lang)
    await message.answer(msg_txt, reply_markup=keyboard, parse_mode="HTML")

    for admin_id in ADMIN_IDS:
        try:
            admin_lang = await get_user_lang(admin_id, db_pool)
            svc_name_translated = get_text(f'service_{service}', admin_lang)
            admin_msg = get_text('admin_notify_new_app', admin_lang, name=f"{name} {surname}", service=svc_name_translated, phone=phone, username=username, date=selected_date.strftime('%d.%m.%Y'), time=selected_time_str)
            await bot.send_message(admin_id, admin_msg, parse_mode="HTML")
        except Exception:
            pass

@client_router.message()
async def catch_all_messages(message: Message, state: FSMContext, db_pool: asyncpg.Pool):
    current_state = await state.get_state()
    lang = await get_user_lang(message.from_user.id, db_pool)
    
    if current_state is None:
        keyboard = await get_main_menu_keyboard(message.from_user.id, db_pool, lang)
        await message.answer(get_text('catch_all_menu', lang), reply_markup=keyboard)
    else:
        await message.answer(get_text('catch_all_input', lang))
