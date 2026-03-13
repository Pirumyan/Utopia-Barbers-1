# Словарь всех текстов бота на трех языках:
# Русском (ru), Армянском (am), Английском (en)

TEXTS = {
    # Главное меню и выбор языка
    'choose_lang': {
        'ru': "Выберите язык интерфейса:",
        'am': "Ընտրեք ինտերֆեյսի լեզուն:",
        'en': "Choose interface language:"
    },
    'main_menu': {
        'ru': "Добро пожаловать! Выберите действие ниже:",
        'am': "Բարի գալուստ! Ընտրեք գործողությունը ստորև:",
        'en': "Welcome! Select an action below:"
    },
    'btn_book': {
        'ru': "Записаться ✂️",
        'am': "Գրանցվել ✂️",
        'en': "Book ✂️"
    },
    'btn_my_apps': {
        'ru': "Мои записи 📅",
        'am': "Իմ գրանցումները 📅",
        'en': "My appointments 📅"
    },
    'btn_back': {
        'ru': "Назад ⬅️",
        'am': "Հետ ⬅️",
        'en': "Back ⬅️"
    },
    'btn_change_lang': {
        'ru': "Сменить язык 🌍",
        'am': "Փոխել լեզուն 🌍",
        'en': "Change language 🌍"
    },
    'btn_cancel': {
        'ru': "Отмена ❌",
        'am': "Չեղարկել ❌",
        'en': "Cancel ❌"
    },
    'btn_cancel_app': {
        'ru': "❌ Отменить запись на {time}",
        'am': "❌ Չեղարկել գրանցումը ժամը {time}",
        'en': "❌ Cancel appointment at {time}"
    },
    
    # Мои записи
    'no_active_apps': {
        'ru': "У вас нет активных записей.",
        'am': "Դուք չունեք ակտիվ գրանցումներ:",
        'en': "You have no active appointments."
    },
    'your_active_apps_title': {
        'ru': "🗓 <b>Ваши активные записи:</b>\n\n",
        'am': "🗓 <b>Ձեր ակտիվ գրանցումները:</b>\n\n",
        'en': "🗓 <b>Your active appointments:</b>\n\n"
    },
    'cancel_too_late': {
        'ru': "Отмена невозможна. До записи осталось менее 1 часа.",
        'am': "Չեղարկումն անհնար է: Մինչև գրանցումը մնացել է 1 ժամից պակաս:",
        'en': "Cancellation impossible. Less than 1 hour left until the appointment."
    },
    'cancel_success': {
        'ru': "Запись успешно отменена!",
        'am': "Գրանցումը հաջողությամբ չեղարկվել է:",
        'en': "Appointment cancelled successfully!"
    },
    'cancel_selected_menu': {
        'ru': "Запись отменена. Выберите действие ниже:",
        'am': "Գրանցումը չեղարկվել է: Ընտրեք գործողությունը ստորև:",
        'en': "Appointment cancelled. Select an action below:"
    },

    # Процесс записи: Выбор услуги
    'max_apps_reached': {
        'ru': "У вас уже есть 2 активные записи. Больше записей создать нельзя.",
        'am': "Դուք արդեն ունեք 2 ակտիվ գրանցում: Այլևս չեք կարող գրանցվել:",
        'en': "You already have 2 active appointments. You cannot create more."
    },
    'choose_service': {
        'ru': "Выберите услугу:",
        'am': "Ընտրեք ծառայությունը:",
        'en': "Choose a service:"
    },
    'service_haircut': {
        'ru': "💇‍♂️ Стрижка (30 мин)",
        'am': "💇‍♂️ Մազերի կտրվածք (30 ր)",
        'en': "💇‍♂️ Haircut (30 min)"
    },
    'service_beard': {
        'ru': "🧔 Борода (15 мин)",
        'am': "🧔 Մորուք (15 ր)",
        'en': "🧔 Beard (15 min)"
    },
    'service_combo': {
        'ru': "🔥 Стрижка + Борода (45 мин)",
        'am': "🔥 Մազերի կտրվածք + Մորուք (45 ր)",
        'en': "🔥 Haircut + Beard (45 min)"
    },

    # Процесс записи: Даты и время
    'no_free_slots': {
        'ru': "К сожалению, свободных мест пока нет.",
        'am': "Ցավոք, ազատ տեղեր դեռ չկան:",
        'en': "Unfortunately, there are no free slots at the moment."
    },
    'choose_date': {
        'ru': "Выберите дату для записи на <b>{service}</b>:",
        'am': "Ընտրեք ամսաթիվ <b>{service}</b>-ի համար:",
        'en': "Choose a date for <b>{service}</b>:"
    },
    'date_full': {
        'ru': "На эту дату слоты нужной длительности закончились.",
        'am': "Այս ամսաթվի համար անհրաժեշտ տևողության տեղերը սպառվել են:",
        'en': "Slots of the required duration for this date are sold out."
    },
    'choose_time': {
        'ru': "Выбрана дата: {date}\nВыберите время:",
        'am': "Ընտրված ամսաթիվ: {date}\nԸնտրեք ժամը:",
        'en': "Selected date: {date}\nChoose time:"
    },
    'time_passed': {
        'ru': "Это время уже прошло.",
        'am': "Այդ ժամանակն արդեն անցել է:",
        'en': "This time has already passed."
    },
    'time_taken': {
        'ru': "Извините, пока вы выбирали, это время уже заняли.",
        'am': "Ներողություն, մինչ դուք ընտրում էիք, այդ ժամն արդեն զբաղեցվել է:",
        'en': "Sorry, while you were choosing, this time was already taken."
    },

    # Процесс записи: Контактные данные
    'ask_name': {
        'ru': "Запись на {date} в {time}.\nПожалуйста, введите ваше Имя:",
        'am': "Գրանցում {date}-ին ժամը {time}-ին:\nԽնդրում ենք մուտքագրել ձեր Անունը:",
        'en': "Appointment on {date} at {time}.\nPlease enter your Name:"
    },
    'err_name': {
        'ru': "Имя слишком короткое. Пожалуйста, напишите ваше настоящее Имя:",
        'am': "Անունը չափազանց կարճ է: Խնդրում ենք գրել ձեր իրական անունը:",
        'en': "Name is too short. Please type your real Name:"
    },
    'ask_surname': {
        'ru': "Теперь введите вашу Фамилию:",
        'am': "Այժմ մուտքագրեք ձեր Ազգանունը:",
        'en': "Now enter your Surname:"
    },
    'err_surname': {
        'ru': "Фамилия слишком короткая. Пожалуйста, напишите вашу настоящую Фамилию:",
        'am': "Ազգանունը չափազանց կարճ է: Խնդրում ենք գրել ձեր իրական ազգանունը:",
        'en': "Surname is too short. Please type your real Surname:"
    },
    'ask_phone': {
        'ru': "И напоследок, введите ваш Номер телефона (только цифры и знак плюс):",
        'am': "Եվ վերջապես, մուտքագրեք ձեր Հեռախոսահամարը:",
        'en': "Lastly, enter your Phone number (numbers and plus sign only):"
    },
    'err_phone': {
        'ru': "Пожалуйста, введите корректный номер телефона:",
        'am': "Խնդրում ենք մուտքագրել ճիշտ հեռախոսահամար:",
        'en': "Please enter a valid phone number:"
    },
    'booking_success': {
        'ru': "✅ Вы успешно записаны на <b>{service}</b>!\n📅 Дата: {date}\n⏰ Время: {time}",
        'am': "✅ Դուք հաջողությամբ գրանցվել եք <b>{service}</b>-ի համար:\n📅 Ամսաթիվ: {date}\n⏰ Ժամ: {time}",
        'en': "✅ You successfully booked a <b>{service}</b>!\n📅 Date: {date}\n⏰ Time: {time}"
    },
    
    # Catch-all
    'catch_all_menu': {
        'ru': "Пожалуйста, используйте кнопки ниже для записи или отмены:",
        'am': "Խնդրում ենք օգտագործել ստորև նշված կոճակները գրանցվելու կամ չեղարկելու համար:",
        'en': "Please use the buttons below to book or cancel:"
    },
    'catch_all_input': {
        'ru': "Пожалуйста, следуйте инструкциям на экране или нажмите /start для сброса.",
        'am': "Խնդրում ենք հետևել էկրանի հրահանգներին կամ սեղմել /start սկզբնական վիճակին վերադառնալու համար:",
        'en': "Please follow the instructions on the screen or press /start to reset."
    },
}

def get_text(key: str, lang: str = 'ru', **kwargs) -> str:
    """Получить текст на нужном языке с форматированием"""
    lang = lang if lang in ['ru', 'am', 'en'] else 'ru'
    text = TEXTS.get(key, {}).get(lang, f"MISSING_{key}")
    if kwargs:
        return text.format(**kwargs)
    return text
