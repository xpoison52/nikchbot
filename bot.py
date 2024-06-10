import telebot
from telebot import types
from telebot.types import LabeledPrice
import datetime
from datetime import *
import re
from config import BOT_TOKEN, PAYMENTS_TOKEN
from config import get_database_connection as db
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.text == '/cancel':
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.send_message(message.chat.id, "Операция отменена. Введите /start, чтобы начать заново.", reply_markup=types.ReplyKeyboardRemove())
        return
    connection = db()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE login = %s and user_id = %s", (message.chat.username, message.chat.id))
    rows = cursor.fetchone()
    if rows == None:
        cursor.execute("insert into users (login, user_id) values (%s, %s)", (message.chat.username, message.chat.id))
    cursor.execute("SELECT * FROM subscriptions WHERE login = %s and user_id = %s", (message.chat.username, message.chat.id))
    rows = cursor.fetchone()
    if rows == None:
        cursor.execute("insert into subscriptions (login, user_id) values (%s, %s)", (message.chat.username, message.chat.id))
    cursor.execute("SELECT * FROM sessions WHERE user_id = %s", (message.chat.id, ))
    rows = cursor.fetchone()
    if rows == None:
        cursor.execute('insert into sessions (user_id) values (%s)', (message.chat.id, ))
    connection.commit()
    now = datetime.now()
    time_now = now.hour
    if time_now >= 0 and time_now < 4:
        greeting = 'Доброй ночи'
    elif time_now >= 4 and time_now < 12:
        greeting = 'Доброе утро'
    elif time_now >= 12 and time_now < 17:
        greeting = 'Добрый день'
    elif time_now >= 17 and time_now < 24:
        greeting = 'Добрый вечер'

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    itembtn1 = types.KeyboardButton('Получить услугу')
    itembtn2 = types.KeyboardButton('База Знаний')
    itembtn3 = types.KeyboardButton('Проверка статуса подписок')
    markup.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, f"{greeting}!\nВыберите чето", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["Получить услугу", "База Знаний", "Проверка статуса подписок", "Связаться с админом"])
def handle_request_type(message):
    if message.text == '/cancel':
        connection = db()
        cursor = connection.cursor()
        cursor.execute('delete from sessions where user_id = %s', (message.chat.id, ))
        connection.commit()
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.send_message(message.chat.id, "Операция отменена. Введите /start, чтобы начать заново.", reply_markup=types.ReplyKeyboardRemove())
        return
    if message.text == "Получить услугу":
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        button_back = telebot.types.InlineKeyboardButton(text="Назад",
                                                     callback_data='back')
        button_ol = telebot.types.InlineKeyboardButton(text="Outline",
                                                     callback_data='Outline')
        button_wg = telebot.types.InlineKeyboardButton(text="WireGuard",
                                                     callback_data='WireGuard')
        button_vless = telebot.types.InlineKeyboardButton(text="Vless",
                                                     callback_data='Vless')
        button_corporative = telebot.types.InlineKeyboardButton(text="Необходима организация корпоративной сети",
                                                     callback_data='corporative')
        keyboard.add(button_ol, button_wg, button_vless, button_corporative)
        keyboard.add(button_back)
        bot.send_message(message.chat.id, "Выберите протокол, либо отправьте заявку на организацию корпоративной сети", reply_markup = keyboard)

    elif message.text == "База Знаний":
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        itembtn1 = types.KeyboardButton('Получить услугу')
        itembtn3 = types.KeyboardButton('Связаться с админом')
        markup.add(itembtn1, itembtn3)
        bot.send_message(message.chat.id, "https://images-cdn.9gag.com/photo/ajAYbXQ_700b.jpg")
        bot.send_message(message.chat.id, "https://i.playground.ru/p/v6Lt6voXVGRVHoAYc3XNtQ.jpeg")
        bot.send_message(message.chat.id, "https://yt3.ggpht.com/a/AGF-l78BC3jcrVna-2P6IeJKhhExBzH_cAGIWXvRLA=s900-c-k-c0xffffffff-no-rj-mo")
        bot.send_message(message.chat.id, "Если Вы нашли нужное решение, можете перейти к выбору услуги кнопкой ниже. Иначе можно связаться с админом для консультации.", reply_markup=markup)
        bot.register_next_step_handler(message, handle_request_type)

    elif message.text == 'Проверка статуса подписок':
        connection = db()
        cursor = connection.cursor()
        cursor.execute("select * from subscriptions where login = 'xpoisonz'")
        res = cursor.fetchone()
        outline_status = res[2]
        outline_date = res[3]
        wireguard_status = res[4]
        wireguard_date = res[5]
        vless_status = res[6]
        vless_date = res[7]
        outline_country = res[8]
        wireguard_country = res[9]
        vless_country = res[10]
        active_subs = 0
        texts = []
        if outline_status != None:
            active_subs += 1
            text_outline = f'Подписка по протоколу Outline:\n\nРегион: {outline_country}\nПодписка истекает: {outline_date}'
            texts.append(text_outline)
        if wireguard_status != None:
            active_subs += 1
            text_wireguard = f'Подписка по протоколу WireGuard:\n\nРегион: {wireguard_country}\nПодписка истекает: {wireguard_date}'
            texts.append(text_wireguard)
        if vless_status != None:
            active_subs += 1
            text_vless = f'Подписка по протоколу WireGuard:\n\nРегион: {vless_country}\nПодписка истекает: {vless_date}'
            texts.append(text_vless)
        if active_subs != 0:
            if active_subs == 1:
                ending = 'активная подписка'
            elif active_subs in [2, 3, 4]:
                ending = 'активных подписки'
            else:
                ending = 'активных подписок'
            bot.send_message(message.chat.id, f"У Вас {active_subs} {ending}:")
            for text in texts:
                bot.send_message(message.chat.id, text)
        else:
            bot.send_message(message.chat.id, f"У Вас нет активных подписок.")
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
        itembtn1 = types.KeyboardButton('Получить услугу')
        itembtn2 = types.KeyboardButton('База Знаний')
        markup.add(itembtn1, itembtn2)
        bot.send_message(message.chat.id, "Выберите следующий шаг", reply_markup = markup)
    elif message.text == 'Связаться с админом':
        bot.send_message(message.chat.id, 'Опишите Ваш вопрос или проблему')
        bot.register_next_step_handler(message, send_to_support)


@bot.callback_query_handler(func=lambda call: call.data == 'Outline' or call.data == 'WireGuard' or call.data == 'Vless' or call.data == 'corporative')
def process_protocol(call):
        connection = db()
        cursor = connection.cursor()
        message = call.message
        chat_id = message.chat.id  
        message_id = message.message_id  
        cursor.execute('update sessions set message_id_1 = %s', (message_id, ))
        connection.commit()
        if call.data == 'corporative':
            bot.send_message(call.message.chat.id, "Для организации корпоротивной сети необходимо связаться с админом. Укажите детали заявки, пожалуйста.")
            bot.register_next_step_handler(message, send_to_support)
        else:
            if call.data == 'Outline':
                msg = 'Outline'
            elif call.data == 'WireGuard':
                msg = 'WireGuard'
            elif call.data == 'Vless':
                msg = 'Vless'
            proto = msg
            cursor.execute('update sessions set proto = %s', (proto, ))
            connection.commit()
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, 
                         text=f'Выбранный протокол - {msg}')
            markup = telebot.types.InlineKeyboardMarkup(row_width=1)
            button_back = telebot.types.InlineKeyboardButton(text="Назад",
                                                     callback_data='backserver')
            button_lat = telebot.types.InlineKeyboardButton(text="Латвия (79р.)",
                                                     callback_data='Latvia')
            button_ger = telebot.types.InlineKeyboardButton(text="Германия (79р.)",
                                                     callback_data='Germany')
            button_tur = telebot.types.InlineKeyboardButton(text="Турция (99р.)",
                                                     callback_data='Turkey')
            markup.add(button_lat, button_ger, button_tur)
            markup.add(button_back)
            bot.send_message(chat_id, "Выберите сервер", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'back')
def handle_back_to_menu(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    send_welcome(call.message)

@bot.callback_query_handler(func=lambda call: call.data == 'backserver')
def handle_back_to_protocol(call):
    conn = db()
    cursor = conn.cursor()
    cursor.execute('select message_id_1 from sessions where user_id = %s', (call.message.chat.id, ))
    message_id = cursor.fetchone()
    message_id = message_id[0]
    print(message_id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=message_id)
    telebot.types.ReplyKeyboardRemove()
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=3)
    button_back = telebot.types.InlineKeyboardButton(text="Назад",
                                                     callback_data='back')
    button_ol = telebot.types.InlineKeyboardButton(text="Outline",
                                                     callback_data='Outline')
    button_wg = telebot.types.InlineKeyboardButton(text="WireGuard",
                                                     callback_data='WireGuard')
    button_vless = telebot.types.InlineKeyboardButton(text="Vless",
                                                     callback_data='Vless')
    keyboard.add(button_ol, button_wg, button_vless)
    keyboard.add(button_back)
    bot.send_message(call.message.chat.id, "Выберите протокол", reply_markup=keyboard)

def send_to_support(message):
    if message.text == '/cancel':
        connection = db()
        cursor = connection.cursor()
        cursor.execute('delete from sessions where user_id = %s', (message.chat.id, ))
        connection.commit()
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.send_message(message.chat.id, "Операция отменена. Введите /start, чтобы начать заново.", reply_markup=types.ReplyKeyboardRemove())
        return
    question = message.text
    support_chat_id = '-1002226636515'
    support_message = f"'{message.chat.id}' \nУебанчик задал вопрос:\n\n{question}"
    bot.send_message(support_chat_id, support_message)   
    bot.send_message(message.chat.id, "Ваш вопрос передан админу. Ожидайте ответа.", reply_markup=types.ReplyKeyboardRemove())

@bot.message_handler(func=lambda message: True)
def handle_group_message(message):
    if message.text == '/cancel':
        connection = db()
        cursor = connection.cursor()
        cursor.execute('delete from sessions where user_id = %s', (message.chat.id, ))
        connection.commit()
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.send_message(message.chat.id, "Операция отменена. Введите /start, чтобы начать заново.", reply_markup=types.ReplyKeyboardRemove())
        return
    
    if message.reply_to_message is not None and message.chat.id == -1002226636515:
        replied_message_text = message.reply_to_message.text
        pattern = r"\'(.*?)\'"
        matches = re.findall(pattern, replied_message_text)
        if matches:
            user_id = matches[0]
            bot.send_message(user_id, f"По вашему вопросу получен ответ от админа:\n\n{message.text}")

@bot.callback_query_handler(func=lambda call: call.data == 'backcountry')
def handle_back_to_country(call):
    conn = db()
    cursor = conn.cursor()
    cursor.execute('select message_id_2 from sessions where user_id = %s', (call.message.chat.id, ))
    message_id = cursor.fetchone()
    message_id = message_id[0]
    print(message_id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=message_id)
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    button_back = telebot.types.InlineKeyboardButton(text="Назад",
                                                     callback_data='backserver')
    button_lat = telebot.types.InlineKeyboardButton(text="Латвия (79р.)",
                                                     callback_data='Latvia')
    button_ger = telebot.types.InlineKeyboardButton(text="Германия (79р.)",
                                                     callback_data='Germany')
    button_tur = telebot.types.InlineKeyboardButton(text="Турция (99р.)",
                                                     callback_data='Turkey')
    markup.add(button_lat, button_ger, button_tur)
    markup.add(button_back)
    bot.send_message(call.message.chat.id, "Выберите сервер", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'Germany' or call.data == 'Latvia' or call.data == 'Turkey')
def get_service(call):
    connection = db()
    cursor = connection.cursor()
    message = call.message
    chat_id = message.chat.id  
    message_id = message.message_id
    if call.data == 'Germany':
        msg = 'Германия'
    elif call.data == 'Latvia':
        msg = 'Латвия'
    elif call.data == 'Turkey':
        msg = 'Турция'
    cursor.execute('update sessions set country = %s', (msg, ))
    connection.commit()
    bot.edit_message_text(chat_id=chat_id, message_id=message_id, 
                    text=f'Выбранный сервер - {msg}')
    cursor.execute('update sessions set message_id_1 = %s', (message_id, ))
    connection.commit()
    if message.text == '/cancel':
        connection = db()
        cursor = connection.cursor()
        cursor.execute('delete from sessions where user_id = %s', (message.chat.id, ))
        connection.commit()
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.send_message(message.chat.id, "Операция отменена. Введите /start, чтобы начать заново.", reply_markup=types.ReplyKeyboardRemove())
        return
    print(id)
    if msg == 'Латвия':
        prices = [LabeledPrice(label='Подписка на VPN Латвия', amount=79*100)]
        keyboard = telebot.types.InlineKeyboardMarkup()
        button_back = telebot.types.InlineKeyboardButton(text="Назад",
                                                     callback_data='backcountry')
        keyboard.add(telebot.types.InlineKeyboardButton("Оплатить", pay=True))
        keyboard.add(button_back)
        bot.send_invoice(
                     message.chat.id,  #chat_id
                     'Подписка на VPN Латвия', #title
                     'Активация VPN Латвия на 1 месяц', #description
                     'HAPPY FRIDAYS COUPON',
                     PAYMENTS_TOKEN, #provider_token
                     'RUB', #currency
                     prices, #prices
                     photo_height=512,
                     photo_width=512,
                     photo_size=512,
                     is_flexible=False,  # True If you need to set up Shipping Fee
                     start_parameter='time-machine-example',
                     reply_markup=keyboard)
    elif msg == 'Германия':
        prices = [LabeledPrice('Подписка на VPN Германия', 79*100)]
        keyboard = telebot.types.InlineKeyboardMarkup()
        button_back = telebot.types.InlineKeyboardButton(text="Назад",
                                                     callback_data='backcountry')
        keyboard.add(telebot.types.InlineKeyboardButton("Оплатить", pay=True))
        keyboard.add(button_back)
        bot.send_invoice(
                     message.chat.id,  #chat_id
                     'Подписка на VPN Германия', #title
                     'Активация VPN Германия на 1 месяц', #description
                     'HAPPY FRIDAYS COUPON',
                     PAYMENTS_TOKEN, #provider_token
                     'RUB', #currency
                     prices, #prices
                     photo_height=512,
                     photo_width=512,
                     photo_size=512,
                     is_flexible=False,  # True If you need to set up Shipping Fee
                     start_parameter='time-machine-example',
                     reply_markup=keyboard)
        
    elif msg == 'Турция':
        prices = [LabeledPrice('Подписка на VPN Турция', 99*100)]
        keyboard = telebot.types.InlineKeyboardMarkup()
        button_back = telebot.types.InlineKeyboardButton(text="Назад",
                                                     callback_data='backcountry')
        keyboard.add(telebot.types.InlineKeyboardButton("Оплатить", pay=True))
        keyboard.add(button_back)
        bot.send_invoice(
                     message.chat.id,  #chat_id
                     'Подписка на VPN Турция', #title
                     'Активация VPN Турция на 1 месяц', #description
                     'HAPPY FRIDAYS COUPON',
                     PAYMENTS_TOKEN, #provider_token
                     'RUB', #currency
                     prices, #prices
                     photo_height=512,
                     photo_width=512,
                     photo_size=512,
                     is_flexible=False,  # True If you need to set up Shipping Fee
                     start_parameter='time-machine-example',
                     reply_markup=keyboard)

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Aliens tried to steal your card's CVV, but we successfully protected your credentials,"
                                                " try to pay again in a few minutes, we need a small rest.")
    
@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    connection = db()
    cursor = connection.cursor()
    delta = timedelta(days=int(30))
    expiry = date.today() + delta
    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
           'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    year,month,day = str(expiry).split('-')
    expiry = f'{day} {months[int(month) - 1]} {year} года'
    cursor.execute('select proto, country from sessions where user_id = %s', (message.chat.id, ))
    info = cursor.fetchone()
    proto = info[0]
    msg = info[1]
    if proto == 'Outline':
        bot.send_message(message.chat.id, 'Оплата прошла успешно! \nВаш код конфигурации:')
        bot.send_message(message.chat.id, 'ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTptMjVHZkFHUEdBWkY0Qm9VeFJjRVZT@195.135.255.173:19651/?outline=1')
        cursor.execute('select outline_status from subscriptions where user_id = %s', (message.chat.id, ))
        yes = cursor.fetchone()
        print(yes)
        if yes[0] == None:
            cursor.execute('update subscriptions set outline_status = True, outline_expires = %s, outline_country = %s', (expiry, msg))
    elif proto == 'WireGuard':
        with open('zazuba777_wg0.conf', 'r', encoding='utf-8') as file:           
            bot.send_message(message.chat.id, 'Оплата прошла успешно! \nВаш файл конфигурации:')
            bot.send_document(message.chat.id, file)
            cursor.execute('select wireguard_status from subscriptions where user_id = %s', (message.chat.id, ))
            yes = cursor.fetchone()
            print(yes)
            if yes[0] == None:
                cursor.execute('update subscriptions set wireguard_status = True, wireguard_expires = %s, wireguard_country = %s', (expiry, msg))
    elif proto == 'Vless':
        bot.send_message(message.chat.id, 'Оплата прошла успешно! \nВаш код конфигурации:')
        bot.send_message(message.chat.id, 'vless://201bbe04-283c-413a-afce-58545097303e@156.67.63.34:31816?type=tcp&security=none#olegal')
        cursor.execute('select vless_status from subscriptions where user_id = %s', (message.chat.id, ))
        yes = cursor.fetchone()
        print(yes)
        if yes[0] == None:
            cursor.execute('update subscriptions set vless_status = True, vless_expires = %s, vless_country = %s', (expiry, msg))
    cursor.execute('delete from sessions where user_id = %s', (message.chat.id, ))
    bot.send_message(message.chat.id, 'Для перехода в главное меню отправьте /start')
    connection.commit()
    cursor.close()
    connection.close()
@bot.message_handler(commands=['cancel'])
def cancel_message(message):

    connection = db()
    cursor = connection.cursor()
    cursor.execute('delete from sessions where user_id = %s', (message.chat.id, ))
    connection.commit()
    if message.text == '/cancel':
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.send_message(message.chat.id, "Операция отменена. Введите /start, чтобы начать заново.", reply_markup=types.ReplyKeyboardRemove())
        return

telebot.apihelper.RETRY_ON_ERROR = True

bot.polling(none_stop=True)