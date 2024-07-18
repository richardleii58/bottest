import os
import random
import string
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

from database import getVerifiedUserIDs, addVerifiedUser, deleteVerifiedUser

# Email configuration
EMAIL_ADDRESS = os.environ['EMAIL_ADDRESS']
EMAIL_PASSWORD = os.environ['EMAIL_PASSWORD']

# Define conversation states
EMAIL, OTP = range(2)

# Dictionary to store OTPs and their confirmation status
user_otps = {}

# List of admin user IDs
ADMIN_USERS = [123456789]  # Replace with actual admin user IDs

def admin_clear_otps(update, context):
    user_id = update.effective_user.id
    if user_id in ADMIN_USERS:
        deleteVerifiedUser()
        # otp_confirmed.clear()
        update.message.reply_text('All OTPs have been cleared.')
    else:
        update.message.reply_text('You do not have permission to use this command.')

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

# handler for dynamic email
def handle_email(update, context):
    user_id = update.effective_user.id
    email = update.message.text.strip()
    
    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        update.message.reply_text('Invalid email address. Please enter a valid email address:')
        return EMAIL
    
    otp = generate_otp()
    user_otps[user_id] = {'otp': otp, 'email': email}  # Store OTP and email in dictionary
    send_email(email, otp)
    update.message.reply_text('An OTP has been sent to your email. Please check and enter it here:')
    return OTP

# Handler for receiving messages
def receive_message(update, context):
    user_id = update.effective_user.id
    entered_otp = update.message.text.strip()
    
    if user_otps.get(user_id) and user_otps[user_id]['otp'] == entered_otp:
        update.message.reply_text('OTP confirmed successfully!')
        addVerifiedUser(user_id)
        return ConversationHandler.END
    else:
        update.message.reply_text('Incorrect OTP. Please try again.')
        return OTP

def cancel(update, context):
    update.message.reply_text('OTP request canceled.')
    return ConversationHandler.END

# Handler for the /otp command
def request_otp(update, context):
    user_id = update.effective_user.id
    if user_id in getVerifiedUserIDs():
        update.message.reply_text('Your OTP has already been confirmed. No need to request a new one.')
        return

    update.message.reply_text('Please enter your email address:')
    return EMAIL

