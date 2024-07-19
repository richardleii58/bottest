from telegram import Update
from telegram.ext import *
from dotenv import load_dotenv
import logging
import os

from buffet import Buffet
from database import executeSQL, addVerifiedUser, getVerifiedUserIDs, deleteVerifiedUser
from channel import broadcast
from otp import *
from telegram import *
load_dotenv()

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

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

def start(update: Update, context: CallbackContext): 
    button = ReplyKeyboardMarkup([[KeyboardButton('/otp'), KeyboardButton('Post something')],[KeyboardButton('/cancel')],[KeyboardButton('/help')]])
    update.message.reply_text("Hello and welcome to BufferClearers Bot! 👋\n\n"
        "This bot is here to help you with various tasks and provide you with seamless interactions. "
        "To access certain features and ensure the security of your account, we require email verification. "
        "Please click the button below to start the verification process. "
        "Once verified, you'll be able to enjoy all the features our bot has to offer!\n\n"
        "If you have any questions or need assistance, feel free to reach out.\n\n"
        "Let's get started!", reply_markup=button)

def help(update: Update, context: CallbackContext): 
    update.message.reply_text(
        
        "Commands\n"
        "/start: First message, teaches users how to use the bot.\n"
        "/help: Brings up a list of commands.\n"
        "/reset, /stop: Resets or stops the bot's current operation.\n"
        "/location: Edits the location. (Displays an error message if no location is set.)\n"
        "/expiry, /time: Edits the time. (Displays an error message if no time is set.)\n"
        "/add_info: Adds or edits additional information.\n"
        "/confirm: Uploads the information to the database.\n"
        "/otp: Authenticates the user.\n"
        "/timings: Provides options to indicate the timing.\n"
        "/cancel: Cancels the OTP verification process.\n"
        "Simply type any command or use the inline buttons to get started!\n\n"
        "For further assistance, contact @lilleiii and our support team."
    )

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
        update.message.reply_text("What are some dietary restrictions?")
        state = "diet"

    elif state == "diet": 
        choose_diet(update, context)

    # if used here cause whenever ready it will just send
    if state == "ready": 
        # give confirmation message
        # allow them to add more info or edit their information 
        update.message.reply_photo(curBuffet['file_id'], f"Location: {curBuffet['location']}\nTime: {curBuffet['expiry']}\nDietary Restrictions: {curBuffet['diet']}")
        print(curBuffet)
        buffetObj = Buffet(curBuffet['file_id'], curBuffet['location'], curBuffet['expiry'], curBuffet['diet'])

        # SENDING IT OFF
        upload(buffetObj)
        broadcast(buffetObj)
        state = "blank"

#diet button
def choose_diet(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Vegetarian", callback_data='Vegetarian')],
        [InlineKeyboardButton("Vegan", callback_data='Vegan')],
        [InlineKeyboardButton("Gluten-Free", callback_data='Gluten-Free')],
        [InlineKeyboardButton("Keto", callback_data='Keto')],
        [InlineKeyboardButton("Paleo", callback_data='Paleo')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose your diet restrictions:', reply_markup=reply_markup)

def dietbutton(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    selected_diet = query.data

    # Update the current buffet with the selected diet
    curBuffet["diet"] = f"#{selected_diet}"
    query.edit_message_text(text=f"You have added your restrictions: {selected_diet}")

    # Move on to the next step
    global state
    state = "ready"

#object processor
def upload(buffetObj):
    # database stuff
    # photo, expiry, location, info
    sql = f"insert into buffet(photo, expiry, location, diet, info) values \
            ('{buffetObj.photo}', '{buffetObj.expiry}', '{buffetObj.location}', '{buffetObj.diet}', NULL);"
    executeSQL(sql)

#photo processor
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
    dp.add_handler(CommandHandler("help", help)) # slash command to help
    dp.add_handler(CommandHandler("admin_clear_otps", admin_clear_otps)) #admin clear
    dp.add_handler(CommandHandler("choose_diet", choose_diet)) #diet button
    dp.add_handler(CallbackQueryHandler(dietbutton))
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