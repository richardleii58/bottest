from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from dotenv import load_dotenv
import logging
import os

logging.basicConfig(
    format = '%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s',
    level = logging.INFO
)

logger = logging.getLogger(__name__)

load_dotenv("./.env")
TOKEN = os.getenv("token")

def start(update: Update, context: CallbackContext):
    if "bye" in update.message.text.lower():
        update.message.reply_text("Goodbye")
    else:
        update.message.reply_text("Hello, World!")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # It handle /start or other slash commands
    # dp.add_handler(CommandHandler("start",start))
    # dp.add_handler(CommandHandler("hi",start))
    # dp.add_handler(CommandHandler("kaishi",start))

    dp.add_handler(MessageHandler(Filters.text, start))
    # if use Filters.all, then even if it is video or photo also will say start

    updater.start_polling()

    Updater.idle()

if __name__ == '__main__':
    main()