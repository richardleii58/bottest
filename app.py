from telegram import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, ConversationHandler
from dotenv import load_dotenv
import logging
import os

from buffet import Buffet
from database import executeSQL, addVerifiedUser, getVerifiedUserIDs
from channel import broadcast
from otp import *

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


TOKEN = os.environ['TOKEN']
# load_dotenv("./.env")
# TOKEN = os.getenv("token")

curBuffet = {} # initiate dictionary? to store the info user is inputting before uploading to database
state = "blank" # i need a variable to track what stage the user is at, to be reset everytime
verified = False

# Define conversation states
EXPIRY, DIETARY_REQUIREMENTS = range(2)

# List of dietary requirements
dietary_requirements = ["Vegetarian", "Vegan", "Gluten-Free", "Nut-Free", "Dairy-Free"]

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

def start(update: Update, context: CallbackContext): 
    update.message.reply_text("Hello and welcome to BufferClearers Bot! 👋\n\n"
        "This bot is here to help you with various tasks and provide you with seamless interactions. "
        "To access certain features and ensure the security of your account, we require email verification. "
        "Please click the button below to start the verification process. "
        "Once verified, you'll be able to enjoy all the features our bot has to offer!\n\n"
        "If you have any questions or need assistance, feel free to reach out.\n\n"
        "Let's get started!")


def handleText(update: Update, context: CallbackContext):
    # else if used so that it only registers one state at a time
    global state
    global verified

    print(state)
    if verified == False:
        # then check if it has been recently verified
        user_id = update.effective_user.id
        verified_users = getVerifiedUserIDs()
        print(user_id)
        print(verified_users)

        if user_id in verified_users:
            verified = True
        else:
            update.message.reply_text("Use /otp to verify")
            return # don't want to let them keep going

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

    #added dietary requirements state, prompted as an inline keyboard button
    elif state == "diet":
        return dietary_requirements_step(update, context)
    
    # if used here cause whenever ready it will just send
    if state == "ready": 
        # give confirmation message
        # allow them to add more info or edit their information 
        update.message.reply_photo(curBuffet['file_id'], f"Location: {curBuffet['location']}\nTime: {curBuffet['expiry']} \nTime: {buffetObj.expiry}\nDietary Restrictions: {buffetObj.diet}")
        print(curBuffet)
        buffetObj = Buffet(curBuffet['file_id'], curBuffet['location'], curBuffet['expiry'], curBuffet['diet'])

        # SENDING IT OFF
        upload(buffetObj)
        broadcast(buffetObj)
        state = "blank"

#displays the dietary requirements as inline buttons.

def dietary_requirements_step(update, context):
    user_id = update.effective_user.id
    curBuffet[user_id] = {"dietary": []}
    
    keyboard = [
        [InlineKeyboardButton(req, callback_data=req) for req in dietary_requirements]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text("Please select your dietary requirements:", reply_markup=reply_markup)
    return DIETARY_REQUIREMENTS

#handles the toggling of dietary requirement selections.
def dietary_requirements_selection(update, context):
    query = update.callback_query
    query.answer()

    user_id = query.message.chat_id
    selected_req = query.data

    if selected_req in curBuffet[user_id]["dietary"]:
        curBuffet[user_id]["dietary"].remove(selected_req)
    else:
        curBuffet[user_id]["dietary"].append(selected_req)
    
    keyboard = [
        [InlineKeyboardButton(f"{'✅ ' if req in curBuffet[user_id]["dietary"] else ''}{req}", callback_data=req) for req in dietary_requirements]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    query.edit_message_text("Please select your dietary requirements:", reply_markup=reply_markup)
    return DIETARY_REQUIREMENTS

def upload(buffetObj):
    # database stuff
    # photo, expiry, location, info
    sql = f"insert into buffet(photo, expiry, location, diet, info) values \
            ('{buffetObj.photo}', '{buffetObj.expiry}', '{buffetObj.location}', {buffetObj.diet}, NULL);"
    executeSQL(sql)


def handlePhoto(update: Update, context: CallbackContext):
    global verified
    if verified == False:
        update.message.reply_text("Use /otp to get started")
        return
    update.message.reply_text("You have uploaded a photo!")
    # turn into blob: https://pynative.com/python-mysql-blob-insert-retrieve-file-image-as-a-blob-in-mysql/#h-what-is-blob
    file_id = update.message.photo[-1].file_id
    curBuffet['file_id'] = file_id
    global state
    state = "location"
    update.message.reply_text("Where is this found?")

def main():
    # transferred these two lines above to test, may need to move back here
    # updater = Updater(TOKEN, use_context=True)
    # dp = updater.dispatcher

    # It handle /start or other slash commands
    dp.add_handler(CommandHandler("start", start)) # slash command to test

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

    dp.add_handler(MessageHandler(Filters.text, handleText))     
    dp.add_handler(MessageHandler(Filters.photo, handlePhoto))
   
    updater.start_polling()

    Updater.idle()

if __name__ == '__main__':
    main()