import telebot
from telebot.types import LabeledPrice, ShippingOption
from config import get_database_connection as db
token = '7198899560:AAHBI0gC3Pj_Z6g12uwALM9tf2Zd7r_6TAo'
provider_token = '1744374395:TEST:2fdbe490c3bc8f784334'  # @BotFather -> Bot Settings -> Payments
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    connection = db()
    cursor = connection.cursor()
    cursor.execute('insert into sessions (user_id) values (%s)', (message.chat.id, ))
    connection.commit()

        



bot.infinity_polling(skip_pending = True)