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
    'err_phone_invalid': {
        'ru': "Номер телефона должен содержать только цифры (и может начинаться с '+'). Буквы не допускаются.",
        'am': "Հեռախոսահամարը պետք է պարունակի միայն թվեր (և կարող է սկսվել '+'-ով): Տառեր չեն թույլատրվում:",
        'en': "Phone number must contain only digits (and can start with '+'). Letters are not allowed."
    },
    'booking_success': {
        'ru': "✅ Вы успешно записаны на <b>{service}</b>!\n📅 Дата: {date}\n⏰ Время: {time}",
        'am': "✅ Դուք հաջողությամբ գրանցվել եք <b>{service}</b>-ի համար:\n📅 Ամսաթիվ: {date}\n⏰ Ժամ: {time}",
        'en': "✅ You successfully booked a <b>{service}</b>!\n📅 Date: {date}\n⏰ Time: {time}"
    },
    
    # Admin Commands
    'admin_no_access': {
        'ru': "У вас нет доступа к этой команде.",
        'am': "Դուք մուտք չունեք այս հրամանին:",
        'en': "You don't have access to this command."
    },
    'admin_format_invalid_date': {
        'ru': "Ошибка формата даты. Используйте DD.MM, например: 14.03",
        'am': "Ամսաթվի ձևաչափի սխալ: Օգտագործեք DD.MM, օրինակ՝ 14.03",
        'en': "Invalid date format. Use DD.MM, e.g.: 14.03"
    },
    'admin_format_invalid_time': {
        'ru': "Неверный формат времени HH:MM.",
        'am': "Ժամանակի սխալ ձևաչափ HH:MM:",
        'en': "Invalid time format HH:MM."
    },
    'admin_format_startday': {
        'ru': "Формат:\n/startday HH:MM HH:MM (на сегодня)\nили\n/startday DD.MM HH:MM HH:MM (на конкретный день)",
        'am': "Ձևաչափ:\n/startday HH:MM HH:MM (այսօրվա համար)\nկամ\n/startday DD.MM HH:MM HH:MM (կոնկրետ օրվա համար)",
        'en': "Format:\n/startday HH:MM HH:MM (for today)\nor\n/startday DD.MM HH:MM HH:MM (for a specific day)"
    },
    'admin_startday_success': {
        'ru': "Рабочий день на {date} создан с {start} до {end}.\nСоздано слотов: {count}.",
        'am': "Աշխատանքային օրը {date}-ի համար ստեղծվել է {start}-ից մինչև {end}:\nՍտեղծված տեղեր՝ {count}:",
        'en': "Workday for {date} created from {start} to {end}.\nSlots created: {count}."
    },
    'admin_format_busy': {
        'ru': "Формат:\n1 слот: /busy HH:MM или /busy DD.MM HH:MM\nНесколько слотов от и до: /busy HH:MM HH:MM или /busy DD.MM HH:MM HH:MM",
        'am': "Ձևաչափ:\n1 տեղ՝ /busy HH:MM կամ /busy DD.MM HH:MM\nՄի քանի տեղ՝ /busy HH:MM HH:MM կամ /busy DD.MM HH:MM HH:MM",
        'en': "Format:\n1 slot: /busy HH:MM or /busy DD.MM HH:MM\nMultiple slots: /busy HH:MM HH:MM or /busy DD.MM HH:MM HH:MM"
    },
    'admin_busy_success_single': {
        'ru': "Время {time} отмечено как занятое на {date}.",
        'am': "{time} ժամը նշվել է որպես զբաղված {date}-ի համար:",
        'en': "Time {time} marked as busy on {date}."
    },
    'admin_busy_success_period': {
        'ru': "Период с {start} до {end} ({count} слотов) отмечен как занятый на {date}.",
        'am': "Ժամանակահատվածը {start}-ից մինչև {end} ({count} տեղ) նշվել է որպես զբաղված {date}-ի համար:",
        'en': "Period from {start} to {end} ({count} slots) marked as busy on {date}."
    },
    'admin_busy_fail': {
        'ru': "Не заблокировано ни одного слота. Проверьте правильность времени от и до.",
        'am': "Ոչ մի տեղ չի արգելափակվել: Ստուգեք ժամանակի ճշտությունը:",
        'en': "No slots were blocked. Check the correctness of the time."
    },
    'admin_format_unbusy': {
        'ru': "Формат:\n1 слот: /unbusy HH:MM или /unbusy DD.MM HH:MM\nНесколько слотов от и до: /unbusy HH:MM HH:MM или /unbusy DD.MM HH:MM HH:MM",
        'am': "Ձևաչափ:\n1 տեղ՝ /unbusy HH:MM կամ /unbusy DD.MM HH:MM\nՄի քանի տեղ՝ /unbusy HH:MM HH:MM կամ /unbusy DD.MM HH:MM HH:MM",
        'en': "Format:\n1 slot: /unbusy HH:MM or /unbusy DD.MM HH:MM\nMultiple slots: /unbusy HH:MM HH:MM or /unbusy DD.MM HH:MM HH:MM"
    },
    'admin_unbusy_success_single': {
        'ru': "Время {time} снова доступно для записи на {date}.",
        'am': "{time} ժամը կրկին հասանելի է գրանցման համար {date}-ին:",
        'en': "Time {time} is available for booking again on {date}."
    },
    'admin_unbusy_success_period': {
        'ru': "Период с {start} до {end} ({count} слотов) снова доступен для записи на {date}.",
        'am': "Ժամանակահատվածը {start}-ից մինչև {end} ({count} տեղ) կրկին հասանելի է գրանցման համար {date}-ին:",
        'en': "Period from {start} to {end} ({count} slots) is available for booking again on {date}."
    },
    'admin_unbusy_fail': {
        'ru': "Слоты не были освобождены. Возможно они и так были свободны или указано неверное время.",
        'am': "Տեղերը չեն ազատվել: Հնարավոր է, որ դրանք արդեն ազատ են կամ նշվել է սխալ ժամանակ:",
        'en': "Slots were not freed. Perhaps they were already free or the wrong time was specified."
    },
    'admin_format_cancel': {
        'ru': "Формат:\n/cancel HH:MM (на сегодня)\nили\n/cancel DD.MM HH:MM (на конкретный день)",
        'am': "Ձևաչափ:\n/cancel HH:MM (այսօրվա համար)\nկամ\n/cancel DD.MM HH:MM (կոնկրետ օրվա համար)",
        'en': "Format:\n/cancel HH:MM (for today)\nor\n/cancel DD.MM HH:MM (for a specific day)"
    },
    'admin_cancel_not_found': {
        'ru': "На {date} в {time} нет записей клиентов.",
        'am': "{date}-ին ժամը {time}-ին հաճախորդների գրանցումներ չկան:",
        'en': "No client appointments on {date} at {time}."
    },
    'admin_cancel_success': {
        'ru': "Запись клиента на {date} в {time} отменена. Слот снова свободен.",
        'am': "Հաճախորդի գրանցումը {date}-ին ժամը {time}-ին չեղարկվել է: Տեղը կրկին ազատ է:",
        'en': "Client appointment on {date} at {time} cancelled. Slot is free again."
    },
    'admin_cancel_notify_client': {
        'ru': "К сожалению запись отменена. Пожалуйста выберите другое время.",
        'am': "Ցավոք, գրանցումը չեղարկվել է: Խնդրում ենք ընտրել այլ ժամանակ:",
        'en': "Unfortunately the appointment was cancelled. Please choose another time."
    },
    'admin_format_dayoff': {
        'ru': "Формат: /dayoff DD.MM",
        'am': "Ձևաչափ: /dayoff DD.MM",
        'en': "Format: /dayoff DD.MM"
    },
    'admin_dayoff_success': {
        'ru': "Все слоты ({count} шт.) на {date} удалены (назначен Выходной).\nКлиентов, чьи записи были отменены: {clients_count}.",
        'am': "Բոլոր տեղերը ({count} հատ) {date}-ի համար հեռացվել են (նշանակված է հանգստյան օր):\nՉեղարկված հաճախորդների քանակը՝ {clients_count}:",
        'en': "All slots ({count} pcs) for {date} deleted (Day Off scheduled).\nClients whose appointments were cancelled: {clients_count}."
    },
    'admin_dayoff_notify_client': {
        'ru': "Здравствуйте, {name}! К сожалению, мы вынуждены отменить вашу запись на {date} в {time} из-за непредвиденного выходного. Приносим свои извинения, пожалуйста, выберите другое время через меню.",
        'am': "Բարև ձեզ, {name}: Ցավոք, մենք ստիպված ենք չեղարկել ձեր գրանցումը {date}-ին ժամը {time}-ին չնախատեսված հանգստյան օրվա պատճառով: Ներողություն ենք խնդրում, խնդրում ենք ընտրել այլ ժամանակ ընտրացանկից:",
        'en': "Hello, {name}! Unfortunately, we have to cancel your appointment on {date} at {time} due to an unforeseen day off. We apologize, please choose another time via the menu."
    },
    'admin_schedule_empty': {
        'ru': "На ближайшие 3 дня записей нет.",
        'am': "Առաջիկա 3 օրվա համար գրանցումներ չկան:",
        'en': "No appointments for the next 3 days."
    },
    'admin_schedule_title': {
        'ru': "🗓 <b>Расписание на ближайшие 3 дня:</b>\n",
        'am': "🗓 <b>Ժամանակացույց առաջիկա 3 օրվա համար՝</b>\n",
        'en': "🗓 <b>Schedule for the next 3 days:</b>\n"
    },
    'admin_format_workday': {
        'ru': "Формат: /workday DD.MM",
        'am': "Ձևաչափ: /workday DD.MM",
        'en': "Format: /workday DD.MM"
    },
    'admin_workday_success': {
        'ru': "Выходной отменен! Стандартный рабочий день на {date} создан (с 10:00 до 21:00).\nВосстановлено слотов: {count}.",
        'am': "Հանգստյան օրը չեղարկվել է: {date}-ի համար ստեղծվել է ստանդարտ աշխատանքային օր (10:00-ից 21:00):\nՎերականգնված տեղեր՝ {count}:",
        'en': "Day off cancelled! Standard workday for {date} created (from 10:00 to 21:00).\nSlots restored: {count}."
    },

    # Admin Notifications
    'admin_notify_new_app': {
        'ru': "✅ Новая запись!\n\nИмя: {name}\nУслуга: {service}\nТелефон: {phone}\nПрофиль: {username}\nДата: {date}\nВремя: {time}",
        'am': "✅ Նոր գրանցում!\n\nԱնուն: {name}\nԾառայություն: {service}\nՀեռախոս: {phone}\nՊրոֆիլ: {username}\nԱմսաթիվ: {date}\nԺամ: {time}",
        'en': "✅ New appointment!\n\nName: {name}\nService: {service}\nPhone: {phone}\nProfile: {username}\nDate: {date}\nTime: {time}"
    },
    'admin_notify_cancel_app': {
        'ru': "❌ Клиент отменил запись\n\nИмя: {name}\nУслуга: {service}\nТелефон: {phone}\nДата: {date}\nВремя: {time}",
        'am': "❌ Հաճախորդը չեղարկել է գրանցումը\n\nԱնուն: {name}\nԾառայություն: {service}\nՀեռախոս: {phone}\nԱմսաթիվ: {date}\nԺամ: {time}",
        'en': "❌ Client cancelled appointment\n\nName: {name}\nService: {service}\nPhone: {phone}\nDate: {date}\nTime: {time}"
    },
}

def get_text(key: str, lang: str = 'ru', **kwargs) -> str:
    """Получить текст на нужном языке с форматированием"""
    lang = lang if lang in ['ru', 'am', 'en'] else 'ru'
    text = TEXTS.get(key, {}).get(lang, f"MISSING_{key}")
    if kwargs:
        return text.format(**kwargs)
    return text
