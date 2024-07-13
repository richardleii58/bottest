import json
import requests
import time
import urllib.parse
import datetime
import os
import psycopg2
from urllib.parse import urlparse
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
##import keep_alive

TOKEN = os.environ['TOKEN']
URL = f"https://api.telegram.org/bot{TOKEN}/"

DATABASE_URL = os.environ['DATABASE_URL']
url = urlparse(DATABASE_URL)
conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)
conn.set_session(readonly=False)  # Ensure the connection is not read-only
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        chat_id BIGINT UNIQUE,
        first_name TEXT,
        date_joined DATE
    );
''')
conn.commit()

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
        url += f"&offset={offset}"
    js = get_json_from_url(url)
    return js

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return text, chat_id

def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + f"sendMessage?text={text}&chat_id={chat_id}&parse_mode=MarkdownV2"
    get_url(url)

def send_message2(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + f"sendMessage?text={text}&chat_id={chat_id}"
    get_url(url)

def send_photo(photo, chat_id, cap):
    photo = urllib.parse.quote_plus(photo)
    url = URL + f"sendPhoto?photo={photo}&chat_id={chat_id}&caption={cap}"
    get_url(url)

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def admin(x):
    print("hello")
    
# Email configuration
EMAIL_ADDRESS = "buffetclearers@gmail.com"
EMAIL_PASSWORD = "untu vjru xpaz kzkq"

# Dictionary to store user OTPs
user_otps = {}

# Function to generate a random OTP
def generate_otp():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

# Function to send OTP via email
def send_email(recipient_email, otp):
    subject = "Your One-Time Password (OTP)"
    body = f"Your OTP is: {otp}"

    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

# Handler for the /start command
def start(update, context):
    update.message.reply_text('Hello! I am your Telegram bot.')

# Handler for receiving messages
def receive_message(update, context):
    user_id = update.effective_user.id
    user_message = update.message.text

    # Check if the user is waiting for OTP confirmation
    if user_id in user_otps:
        # Check if the received message matches the OTP
        if user_message == user_otps[user_id]:
            update.message.reply_text('OTP verified successfully!')
            del user_otps[user_id]  # Remove OTP from dictionary
        else:
            update.message.reply_text('Invalid OTP! Please try again.')

# Handler for the /otp command
def request_otp(update, context):
    user_id = update.effective_user.id
    email = "leirichard58@gmail.com"  # Replace with user's email address
    otp = generate_otp()
    user_otps[user_id] = otp  # Store OTP in dictionary
    send_email(email, otp)
    update.message.reply_text('An OTP has been sent to your email. Please check and enter it here.')

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("otp", request_otp))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, receive_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
