from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters

def start(update: Update, context: CallbackContext): 
    # test, to delete
    if "bye" in update.message.text.lower():
        update.message.reply_text("Goodbye")
    else:
        update.message.reply_text("Hello, World!")


def introduce(update: Update, context: CallbackContext):
    update.message.reply_text("Available commands:\n"
                              "/start - Start the bot\n"
                              "/help - Display available commands\n"
                              "/cat - Get a random cat picture")