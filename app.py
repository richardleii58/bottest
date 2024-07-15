from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv
import logging
import os

from slashCommands import start, introduce
from buffet import Buffet
from database import executeSQL
from channel import broadcast
from otp import request_otp, handle_email, receive_message, cancel, EMAIL, OTP


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
    print(state)

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
        curBuffet["expiry"] = update.message.text # change this to buttons instead
        update.message.reply_text("You have entered a time!")
        # expiry date successful added, move on to next step
        state = "ready"

    # if used here cause whenever ready it will just send
    if state == "ready": 
        # give confirmation message
        # allow them to add more info or edit their information 
        update.message.reply_photo(curBuffet['file_id'], f"Location: {curBuffet['location']}\nTime: {curBuffet['expiry']}")
        print(curBuffet)
        buffetObj = Buffet(curBuffet['file_id'], curBuffet['location'], curBuffet['expiry'])

        # SENDING IT OFF
        upload(buffetObj)
        broadcast(buffetObj)
        state = "blank"


def upload(buffetObj):
    # database stuff
    # photo, expiry, location, info
    sql = f"insert into buffet(photo, expiry, location, info) values \
            ('{buffetObj.photo}', '{buffetObj.expiry}', '{buffetObj.location}', NULL);"
    # sql = f"insert into buffet values ('{curBuffet['file_id']}', '{curBuffet['location']}', '{curBuffet['expiry']}', NULL);"values
    # print(sql)
    executeSQL(sql)


def handlePhoto(update: Update, context: CallbackContext):
    update.message.reply_text("You have uploaded a photo!")
    # turn into blob: https://pynative.com/python-mysql-blob-insert-retrieve-file-image-as-a-blob-in-mysql/#h-what-is-blob
    file_id = update.message.photo[-1].file_id
    curBuffet['file_id'] = file_id
    global state
    state = "location"
    update.message.reply_text("Where is this found?")



user_ids = []
def user_verified(user_id):
    if user_id in user_ids:
        print("user id found")
        return True
    else:
        print("user id not found")
        return False 

def verify(update: Update, context: CallbackContext):
    global user_ids
    user_id = update.effective_user.id
    user_ids.append(user_id)  
    print("after verify (in command)", user_ids)
    dp.add_handler(MessageHandler(Filters.text, handleText))     
    dp.add_handler(MessageHandler(Filters.photo, handlePhoto))



def main():
    # transferred these two lines above to test, may need to move back here
    # updater = Updater(TOKEN, use_context=True)
    # dp = updater.dispatcher
    print("at the start, user_ids", user_ids)

    # It handle /start or other slash commands
    dp.add_handler(CommandHandler("start", start)) # slash command to test
    dp.add_handler(CommandHandler("verify", verify)) # slash command to test

    # otp stuff from richard
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('otp', request_otp)],
        states={
            EMAIL: [MessageHandler(Filters.text & ~Filters.command, handle_email)],
            OTP: [MessageHandler(Filters.text & ~Filters.command, receive_message)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    # dp.add_handler(CommandHandler("clear_otps", admin_clear_otps))
    dp.add_handler(conv_handler)

    user_id = "test"
    if user_verified(user_id): 
        print("verified")
        print("current user_ids", user_ids)
        dp.add_handler(MessageHandler(Filters.text, handleText))     
        dp.add_handler(MessageHandler(Filters.photo, handlePhoto))
        # may have future problem if you want to upload multiple photographs
    else:
        print("not verified")
        print("current user_ids", user_ids)

   
    updater.start_polling()

    Updater.idle()

if __name__ == '__main__':
    main()