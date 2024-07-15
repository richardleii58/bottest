from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from dotenv import load_dotenv
import logging
import os

from slashCommands import start, introduce
from buffet import Buffet
from database import executeSQL

logging.basicConfig(
    format = '%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s',
    level = logging.INFO
)

logger = logging.getLogger(__name__)

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

def write_file(data, filename):
    # Convert binary data to proper format and write it on Hard Disk
    with open(filename, 'wb') as file:
        file.write(data)

load_dotenv("./.env")
TOKEN = os.getenv("token")

curBuffet = {} # initiate dictionary? to store the info user is inputting before uploading to database
state = "blank" # i need a variable to track what stage the user is at, to be reset everytime

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

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
        update.message.reply_photo(curBuffet['photo'], f"Location: {curBuffet['location']}\nTime: {curBuffet['expiry']}")
        print(curBuffet)
        buffetObj = Buffet(curBuffet['photo'], curBuffet['location'], curBuffet['expiry'])
        upload(buffetObj)

def upload(buffetObj):
    # database stuff
    # photo, expiry, location, info
    sql = f"insert into buffet(photo, expiry, location, info) values \
            ('{buffetObj.photo}', '{buffetObj.expiry}', '{buffetObj.location}', NULL);"
    # sql = f"insert into buffet values ('{curBuffet['photo']}', '{curBuffet['location']}', '{curBuffet['expiry']}', NULL);"values
    # print(sql)
    executeSQL(sql)


def handlePhoto(update: Update, context: CallbackContext):
    update.message.reply_text("You have uploaded a photo!")
    # turn into blob: https://pynative.com/python-mysql-blob-insert-retrieve-file-image-as-a-blob-in-mysql/#h-what-is-blob
    file_id = update.message.photo[-1].file_id
    curBuffet['photo'] = file_id
    global state
    state = "location"
    update.message.reply_text("Where is this found?")


def main():
    # transferred these two lines above to test, may need to move back here
    # updater = Updater(TOKEN, use_context=True)
    # dp = updater.dispatcher

    # It handle /start or other slash commands
    dp.add_handler(CommandHandler("start", introduce)) # slash command to test
    dp.add_handler(CommandHandler("kaishi", start)) # slash command to test


    dp.add_handler(MessageHandler(Filters.text, handleText))     
    dp.add_handler(MessageHandler(Filters.photo, handlePhoto))
        # may have future problem if you want to upload multiple photographs
    
    updater.start_polling()

    Updater.idle()

if __name__ == '__main__':
    main()