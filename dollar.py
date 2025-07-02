import telebot
import requests
import re
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '...'  
bot = telebot.TeleBot(TOKEN)


def get_usdt_uah():
    url = "https://api.binance.com/api/v3/ticker/price?symbol=USDTUAH"
    response = requests.get(url)
    if response.status_code == 200:
        return float(response.json()['price'])
    return None


def main_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('📈 Актуальний курс', callback_data='get_rate'))
    markup.add(InlineKeyboardButton('➕ Підключити чат', url=f"https://t.me/{bot.get_me().username}?startgroup=true"))
    markup.add(InlineKeyboardButton('💱 Обмін', callback_data='exchange'))
    return markup


def back_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('🔙 Назад', callback_data='back'))
    return markup


def exchange_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('💱 Обмін', url='https://t.me/...'))  
    markup.add(InlineKeyboardButton('🔙 Назад', callback_data='back'))
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Привіт! Я допоможу тобі дізнатись актуальний курс USDT/UAH", reply_markup=main_menu())


@bot.message_handler(commands=['курс'])
@bot.message_handler(func=lambda message: message.text.lower() in ["який курс?", "курс?", "курс"])
def send_exchange_rate(message):
    chat_id = message.chat.id
    rate = get_usdt_uah()
    
    if rate:
        text = f"🔹 Актуальний курс USDT: {rate} UAH"
    else:
        text = "❌ Не вдалося отримати курс."

    bot.send_message(chat_id, text)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'get_rate':  
        rate = get_usdt_uah()
        if rate:
            text = f"🔹 Актуальний курс USDT: {rate} UAH"
        else:
            text = "❌ Не вдалося отримати курс."
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back_markup())

    elif call.data == 'exchange':  
        text = "💱 Ми можемо швидко обміняти вашу криптовалюту.\n\nНапишіть нам з чітко сформульованим запитом обміну.\n\nПриклад: треба обміняти 500 USDT"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=exchange_markup())

    elif call.data == 'back':  
        bot.edit_message_text("👋 Привіт! Я допоможу тобі дізнатись актуальний курс USDT/UAH", 
                              call.message.chat.id, call.message.message_id, reply_markup=main_menu())


@bot.message_handler(func=lambda message: bool(re.match(r'^\d+(\.\d+)?\s?(usdt|грн)$', message.text.lower())))
def convert_currency(message):
    text = message.text.lower()
    rate = get_usdt_uah()
    
    if not rate:
        bot.reply_to(message, "❌ Не вдалося отримати курс. Спробуйте пізніше.")
        return
    
    amount_match = re.match(r'^(\d+(\.\d+)?)\s?(usdt|грн)$', text)
    amount = float(amount_match.group(1)) 
    currency_type = amount_match.group(3) 

    if currency_type == "usdt":
        total_uah = round(amount * rate, 2)  
        bot.reply_to(message, f"💱 {amount} USDT ≈ {total_uah} UAH за поточним курсом {rate} UAH/USDT")
    else:
        total_usdt = round(amount / rate, 2)  
        bot.reply_to(message, f"💱 {amount} UAH ≈ {total_usdt} USDT за поточним курсом {rate} UAH/USDT")


bot.polling(none_stop=True)
