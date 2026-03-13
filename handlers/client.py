from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import date, datetime, timedelta, time
import asyncpg
from config import ADMIN_IDS

client_router = Router()

class BookingState(StatesGroup):
    waiting_for_name = State()
    waiting_for_surname = State()
    waiting_for_phone = State()

# Главное меню
@client_router.message(Command("start"))
async def cmd_start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Записаться ✂️", callback_data="book_start")]
    ])
    await message.answer("Добро пожаловать в барбершоп! Нажмите кнопку ниже, чтобы записаться.", reply_markup=keyboard)

@client_router.callback_query(F.data == "book_start")
async def start_booking(callback: CallbackQuery, db_pool: asyncpg.Pool):
    today = date.today()
    
    async with db_pool.acquire() as conn:
        # Проверяем антиспам (максимум 2 активные записи)
        active_count = await conn.fetchval('''
            SELECT COUNT(*) FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE u.telegram_id = $1 AND a.status = 'booked' AND a.date >= $2
        ''', callback.from_user.id, today)

        if active_count and active_count >= 2:
            await callback.answer("У вас уже есть 2 активные записи. Больше записей создать нельзя.", show_alert=True)
            return

        # Ищем свободные слоты на сегодня
        slots = await conn.fetch('''
            SELECT time FROM appointments 
            WHERE date = $1 AND status = 'free' 
            ORDER BY time
        ''', today)

    if not slots:
        await callback.message.edit_text("К сожалению, на сегодня нет свободных мест.")
        return

    # Генерируем клавиатуру со слотами
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
        
    buttons.append([InlineKeyboardButton(text="Отмена ❌", callback_data="cancel_booking")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    await callback.message.edit_text("Выберите свободное время на сегодня:", reply_markup=keyboard)

@client_router.callback_query(F.data.startswith("select_time_"))
async def select_time(callback: CallbackQuery, state: FSMContext, db_pool: asyncpg.Pool):
    selected_time = callback.data.split("_")[2]
    today = date.today()

    # Проверка, не заняли ли слот пока пользователь думал
    async with db_pool.acquire() as conn:
        slot = await conn.fetchrow('''
            SELECT status FROM appointments WHERE date = $1 AND time = $2::time
        ''', today, selected_time)

    if not slot or slot['status'] != 'free':
        await callback.answer("Это время уже занято.", show_alert=True)
        # Перезагружаем слоты
        await start_booking(callback, db_pool)
        return

    await state.update_data(selected_time=selected_time, selected_date=today)
    await state.set_state(BookingState.waiting_for_name)
    await callback.message.edit_text(f"Время {selected_time} свободно. Пожалуйста, введите ваше Имя:")

@client_router.message(BookingState.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(BookingState.waiting_for_surname)
    await message.answer("Теперь введите вашу Фамилию:")

@client_router.message(BookingState.waiting_for_surname)
async def process_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await state.set_state(BookingState.waiting_for_phone)
    await message.answer("И напоследок, введите ваш Номер телефона:")

@client_router.message(BookingState.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext, db_pool: asyncpg.Pool, bot: Bot):
    user_data = await state.get_data()
    phone = message.text
    name = user_data['name']
    surname = user_data['surname']
    selected_time = user_data['selected_time']
    selected_date = user_data['selected_date']

    tg_id = message.from_user.id

    async with db_pool.acquire() as conn:
        # Сохраняем или обновляем пользователя
        user_id = await conn.fetchval('''
            INSERT INTO users (telegram_id, name, surname, phone)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (telegram_id) DO UPDATE 
            SET name = EXCLUDED.name, surname = EXCLUDED.surname, phone = EXCLUDED.phone
            RETURNING id
        ''', tg_id, name, surname, phone)

        # Пытаемся занять слот. Если rows updated == 0, значит его кто-то уже занял.
        result = await conn.execute('''
            UPDATE appointments SET status = 'booked', user_id = $1
            WHERE date = $2 AND time = $3::time AND status = 'free'
        ''', user_id, selected_date, selected_time)

    if result == "UPDATE 0":
        await message.answer("К сожалению, это время уже занято. Пожалуйста, начните заново /start")
        await state.clear()
        return

    await message.answer(f"Спасибо! Ваша запись подтверждена.\nДата: {selected_date.strftime('%d.%m.%Y')}\nВремя: {selected_time}")
    
    # Уведомление админам
    admin_msg = f"🔔 Новая запись!\n\nИмя: {name}\nФамилия: {surname}\nТелефон: {phone}\nДата: {selected_date.strftime('%d.%m.%Y')}\nВремя: {selected_time}"
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_msg)
        except Exception:
            pass

    await state.clear()


@client_router.callback_query(F.data == "cancel_booking")
async def cancel_booking_process(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Запись прервана.")

# Отмена записи клиентом (команда /my_cancel)
@client_router.message(Command("my_cancel"))
async def client_cancel(message: Message, db_pool: asyncpg.Pool, bot: Bot):
    today = date.today()
    now_time = datetime.now()

    async with db_pool.acquire() as conn:
        # Ищем активную запись пользователя на сегодня
        appointment = await conn.fetchrow('''
            SELECT a.id, a.date, a.time, u.name, u.surname, u.phone
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE u.telegram_id = $1 AND a.status = 'booked' AND a.date >= $2
            ORDER BY a.date, a.time LIMIT 1
        ''', message.from_user.id, today)

        if not appointment:
            await message.answer("У вас сейчас нет активных записей.")
            return

        # Проверяем, осталось ли больше 1 часа
        appointment_datetime = datetime.combine(appointment['date'], appointment['time'])
        if appointment_datetime - now_time < timedelta(hours=1):
            await message.answer("Отмена невозможна. До записи осталось менее 1 часа.")
            
            # Уведомление админа о попытке отмены
            admin_msg = f"⚠️ Попытка отмены менее чем за час!\nКлиент: {appointment['name']} {appointment['surname']} ({appointment['phone']})\nЗапись: {appointment['time'].strftime('%H:%M')}"
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

    await message.answer("Ваша запись успешно отменена.")

    # Уведомление админа
    admin_msg = f"❌ Клиент отменил запись\n\nИмя: {appointment['name']}\nФамилия: {appointment['surname']}\nТелефон: {appointment['phone']}\nДата: {appointment['date'].strftime('%d.%m.%Y')}\nВремя: {appointment['time'].strftime('%H:%M')}"
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_msg)
        except Exception:
            pass
