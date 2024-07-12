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

curBuffet = {} # initiate dictionary? to store the info user is inputting before uploading to database
state = "blank" # i need a variable to track what stage the user is at, to be reset everytime

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

def start(update: Update, context: CallbackContext): 
    # test, to delete
    if "bye" in update.message.text.lower():
        update.message.reply_text("Goodbye")
    else:
        update.message.reply_text("Hello, World!")

def handleText(update: Update, context: CallbackContext):
    # else if used so that it only registers one state at a time
    global state

    if state == "blank":
        # this means that the user has not done anything yet
        update.message.reply_text("Upload a picture of the food to get started.")

    elif state == "location": 
        # now we want a location
        if len(update.message.text.lower()) < 10: # may not keep this
            update.message.reply_text("Please enter more information!")
        else:
            curBuffet["location"] = update.message.text
            update.message.reply_text("You have entered a location!")
            # location successful added, move on to next step
            update.message.reply_text("When does this have to be cleared by?")
            state = "expiry"

    elif state == "expiry": 
        # may need to add checks here to verify that it's correct
        curBuffet["expiry"] = update.message.text
        update.message.reply_text("You have entered a time!")
        # expiry date successful added, move on to next step
        state = "ready"

    # if used here cause whenever ready it will just send
    if state == "ready": 
        # give confirmation message
        # allow them to add more info or edit their information 
        update.message.reply_text(f"Location: {curBuffet['location']}\nTime: {curBuffet['expiry']}!")
        print(curBuffet)

def introduce(update: Update, context: CallbackContext):
    update.message.reply_text("Available commands:\n"
                              "/start - Start the bot\n"
                              "/help - Display available commands\n"
                              "/cat - Get a random cat picture")



def handlePhoto(update: Update, context: CallbackContext):
    update.message.reply_text("You have uploaded a photo!")
    # turn into blob: https://pynative.com/python-mysql-blob-insert-retrieve-file-image-as-a-blob-in-mysql/#h-what-is-blob
    curBuffet["photo"] = "PHOTO PLACEHOLDER"

    global state
    state = "location"
    update.message.reply_text("Where is this found?")
    

def main():
    # transferred these two lines above to test, may need to move back here
    # updater = Updater(TOKEN, use_context=True)
    # dp = updater.dispatcher

    # It handle /start or other slash commands
    dp.add_handler(CommandHandler("start",introduce))
    # dp.add_handler(CommandHandler("hi",start))
    # dp.add_handler(CommandHandler("kaishi",start))

    startHandler = MessageHandler(Filters.text, handleText)
    dp.add_handler(startHandler) # this code runs hello world if you say anything under than bye
    # if use Filters.all, then even if it is video or photo also will say start
    dp.add_handler(MessageHandler(Filters.photo, handlePhoto))

    updater.start_polling()

    Updater.idle()

if __name__ == '__main__':
    main()