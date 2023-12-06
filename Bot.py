import aiogram
import sqlite3

from aiogram import Bot, Dispatcher, types
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@bot.copy_message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('data.db')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (ID INT auto_increment primary key, UserID BIGINT, OrderTime BIGINT, FirstName STRING, LastName STRING, PhoneNumber BIGINT, City STRING, PostalNumber BIGINT, Order STRING)')
    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Привет')
    bot.register_next_step_handler(message, user_name)

def user_name(message):
    name = message.text.strip()
    bot.send_message(message.chat.id, 'Логин')
    bot.register_next_step_handler(message, user_name)

bot.polling(none_stop=True)