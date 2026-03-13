from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import date, datetime, timedelta, time
import asyncpg
from config import ADMIN_IDS, YEREVAN_TZ

client_router = Router()

class BookingState(StatesGroup):
    waiting_for_date = State()
    waiting_for_time = State()
    waiting_for_name = State()
    waiting_for_surname = State()
    waiting_for_phone = State()

def get_yerevan_now():
    return datetime.now(YEREVAN_TZ)

@client_router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Записаться ✂️", callback_data="book_start")]
    ])
    await message.answer("Добро пожаловать в барбершоп! Нажмите кнопку ниже, чтобы записаться.", reply_markup=keyboard)

@client_router.callback_query(F.data == "book_start")
async def start_booking(callback: CallbackQuery, db_pool: asyncpg.Pool):
    now_dt = get_yerevan_now()
    today = now_dt.date()
    now_time = now_dt.time()
    
    async with db_pool.acquire() as conn:
        active_count = await conn.fetchval('''
            SELECT COUNT(*) FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE u.telegram_id = $1 AND a.status = 'booked' AND (a.date > $2 OR (a.date = $2 AND a.time > $3))
        ''', callback.from_user.id, today, now_time)

        if active_count and active_count >= 2:
            await callback.answer("У вас уже есть 2 активные записи. Больше записей создать нельзя.", show_alert=True)
            return

        dates_records = await conn.fetch('''
            SELECT DISTINCT date FROM appointments 
            WHERE status = 'free' AND (date > $1 OR (date = $1 AND time > $2))
            ORDER BY date
        ''', today, now_time)

    if not dates_records:
        await callback.message.edit_text("К сожалению, свободных мест пока нет.")
        return

    buttons = []
    row = []
    for record in dates_records:
        d = record['date']
        date_str = d.strftime('%d.%m')
        btn_data = f"select_date_{d.isoformat()}"
        row.append(InlineKeyboardButton(text=date_str, callback_data=btn_data))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
        
    buttons.append([InlineKeyboardButton(text="Отмена ❌", callback_data="cancel_booking")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text("Выберите дату для записи:", reply_markup=keyboard)

@client_router.callback_query(F.data.startswith("select_date_"))
async def select_date(callback: CallbackQuery, state: FSMContext, db_pool: asyncpg.Pool):
    selected_date_iso = callback.data.split("_")[2]
    selected_date = date.fromisoformat(selected_date_iso)
    
    now_dt = get_yerevan_now()
    today = now_dt.date()
    now_time = now_dt.time()

    async with db_pool.acquire() as conn:
        # Ищем слоты на эту дату
        if selected_date == today:
            slots = await conn.fetch('''
                SELECT time FROM appointments 
                WHERE date = $1 AND status = 'free' AND time > $2
                ORDER BY time
            ''', selected_date, now_time)
        else:
            slots = await conn.fetch('''
                SELECT time FROM appointments 
                WHERE date = $1 AND status = 'free'
                ORDER BY time
            ''', selected_date)

    if not slots:
        await callback.answer("На эту дату слоты закончились.", show_alert=True)
        await start_booking(callback, db_pool)
        return

    await state.update_data(selected_date=selected_date_iso)

    buttons = []
    row = []
    for slot in slots:
        slot_time_str = slot['time'].strftime('%H:%M')
        row.append(InlineKeyboardButton(text=slot_time_str, callback_data=f"select_time_{slot_time_str}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
        
    buttons.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="book_start"),
        InlineKeyboardButton(text="Отмена ❌", callback_data="cancel_booking")
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text(f"Выбрана дата: {selected_date.strftime('%d.%m')}\nВыберите время:", reply_markup=keyboard)

@client_router.callback_query(F.data.startswith("select_time_"))
async def select_time(callback: CallbackQuery, state: FSMContext, db_pool: asyncpg.Pool):
    user_data = await state.get_data()
    selected_date_str = user_data.get('selected_date')
    if not selected_date_str:
        await callback.answer("Сначала выберите дату.", show_alert=True)
        await start_booking(callback, db_pool)
        return

    selected_date = date.fromisoformat(selected_date_str)
    selected_time_str = callback.data.split("_")[2]
    hour, minute = map(int, selected_time_str.split(':'))
    selected_time_obj = time(hour, minute)

    now_dt = get_yerevan_now()
    today = now_dt.date()
    now_time = now_dt.time()

    if selected_date < today or (selected_date == today and selected_time_obj <= now_time):
        await callback.answer("Это время уже прошло.", show_alert=True)
        await start_booking(callback, db_pool)
        return

    async with db_pool.acquire() as conn:
        slot = await conn.fetchrow('''
            SELECT status FROM appointments WHERE date = $1 AND time = $2
        ''', selected_date, selected_time_obj)

    if not slot or slot['status'] != 'free':
        await callback.answer("Это время уже занято.", show_alert=True)
        await start_booking(callback, db_pool)
        return

    await state.update_data(selected_time=selected_time_str)
    await state.set_state(BookingState.waiting_for_name)
    await callback.message.edit_text(f"Запись на {selected_date.strftime('%d.%m')} в {selected_time_str}.\nПожалуйста, введите ваше Имя:")

@client_router.message(BookingState.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    if len(text) < 2:
        await message.answer("Имя слишком короткое. Пожалуйста, напишите ваше настоящее Имя:")
        return
    await state.update_data(name=text)
    await state.set_state(BookingState.waiting_for_surname)
    await message.answer("Теперь введите вашу Фамилию:")

@client_router.message(BookingState.waiting_for_surname)
async def process_surname(message: Message, state: FSMContext):
    text = message.text.strip() if message.text else ""
    if len(text) < 2:
        await message.answer("Фамилия слишком короткая. Пожалуйста, напишите вашу настоящую Фамилию:")
        return
    await state.update_data(surname=text)
    await state.set_state(BookingState.waiting_for_phone)
    await message.answer("И напоследок, введите ваш Номер телефона (только цифры и знак плюс):")

@client_router.message(BookingState.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext, db_pool: asyncpg.Pool, bot: Bot):
    phone = message.text.strip() if message.text else ""
    if len(phone) < 5:
        await message.answer("Пожалуйста, введите корректный номер телефона:")
        return

    user_data = await state.get_data()
    name = user_data['name']
    surname = user_data['surname']
    selected_time_str = user_data['selected_time']
    hour, minute = map(int, selected_time_str.split(':'))
    selected_time_obj = time(hour, minute)
    selected_date = date.fromisoformat(user_data['selected_date'])

    tg_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else f'<a href="tg://user?id={tg_id}">Профиль клиента</a>'

    async with db_pool.acquire() as conn:
        user_id = await conn.fetchval('''
            INSERT INTO users (telegram_id, name, surname, phone)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (telegram_id) DO UPDATE 
            SET name = EXCLUDED.name, surname = EXCLUDED.surname, phone = EXCLUDED.phone
            RETURNING id
        ''', tg_id, name, surname, phone)

        result = await conn.execute('''
            UPDATE appointments SET status = 'booked', user_id = $1
            WHERE date = $2 AND time = $3 AND status = 'free'
        ''', user_id, selected_date, selected_time_obj)

    if result == "UPDATE 0":
        await message.answer("К сожалению, это время уже занято другим клиентом. Выберите другое время /start")
        await state.clear()
        return

    await message.answer(f"Спасибо! Ваша запись подтверждена.\nДата: {selected_date.strftime('%d.%m.%Y')}\nВремя: {selected_time_str}")
    
    admin_msg = f"🔔 Новая запись!\n\nИмя: {name}\nФамилия: {surname}\nТелефон: {phone}\nАккаунт: {username}\nДата: {selected_date.strftime('%d.%m.%Y')}\nВремя: {selected_time_str}"
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_msg, parse_mode="HTML")
        except Exception:
            pass

    await state.clear()


@client_router.callback_query(F.data == "cancel_booking")
async def cancel_booking_process(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Запись прервана.")

@client_router.message(Command("my_cancel"))
async def client_cancel(message: Message, db_pool: asyncpg.Pool, bot: Bot):
    now_dt = get_yerevan_now()
    today = now_dt.date()
    now_time = now_dt.time()

    async with db_pool.acquire() as conn:
        # Ищем только будущие активные записи
        appointment = await conn.fetchrow('''
            SELECT a.id, a.date, a.time, u.name, u.surname, u.phone
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE u.telegram_id = $1 AND a.status = 'booked' AND (a.date > $2 OR (a.date = $2 AND a.time > $3))
            ORDER BY a.date, a.time LIMIT 1
        ''', message.from_user.id, today, now_time)

        if not appointment:
            await message.answer("У вас нет предстоящих записей, которые можно было бы отменить.")
            return

        app_dt = datetime.combine(appointment['date'], appointment['time'], tzinfo=YEREVAN_TZ)
        
        # Разница во времени
        if app_dt - now_dt < timedelta(hours=1):
            await message.answer(f"Отмена невозможна. Ваша запись состоится {appointment['date'].strftime('%d.%m')} в {appointment['time'].strftime('%H:%M')}, до неё осталось менее 1 часа.")
            
            admin_msg = f"⚠️ Попытка отмены менее чем за час!\nКлиент: {appointment['name']} {appointment['surname']} ({appointment['phone']})\nЗапись: {appointment['date'].strftime('%d.%m')} в {appointment['time'].strftime('%H:%M')}"
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(admin_id, admin_msg)
                except Exception:
                    pass
            return

        # Отменяем (слот становится free)
        await conn.execute('''
            UPDATE appointments SET status = 'free', user_id = NULL WHERE id = $1
        ''', appointment['id'])

    await message.answer(f"Ваша запись на {appointment['date'].strftime('%d.%m')} в {appointment['time'].strftime('%H:%M')} успешно отменена.")

    admin_msg = f"❌ Клиент отменил запись\n\nИмя: {appointment['name']}\nФамилия: {appointment['surname']}\nТелефон: {appointment['phone']}\nДата: {appointment['date'].strftime('%d.%m.%Y')}\nВремя: {appointment['time'].strftime('%H:%M')}"
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_msg)
        except Exception:
            pass
