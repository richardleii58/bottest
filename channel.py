# for the sending of stuff only
import telegram
import os
from dotenv import load_dotenv

load_dotenv("./.env")
TOKEN = os.getenv("token")
# CHAT_ID = os.getenv("chat_id")
# get list of chat ids from database later. now is a string in .env
CHAT_IDS = os.getenv("chat_ids")

def convert_to_list(str):
    new_str = str.strip('[').strip(']')
    list = new_str.split(',')
    new_list = []
    for item in list:
        new_list.append(item.strip())
    return new_list



def broadcast(buffetObj, chat_ids = CHAT_IDS, token = TOKEN):
    bot = telegram.Bot(TOKEN)

    for chat_id in chat_ids:
        bot.sendPhoto(chat_id, buffetObj.photo, f"Location: {buffetObj.location}\nTime: {buffetObj.expiry}")

# def send(msg, chat_id = CHAT_ID, token = TOKEN):
#     """
#     Send a message to a telegram user or group specified on chatId
#     chat_id must be a number!
#     """
#     bot = telegram.Bot(token)
#     bot.sendMessage(chat_id, text=msg)
