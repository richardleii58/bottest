# BuffetClearerBot

## Description
BuffetClearerBot is a Telegram bot that verifies users and allows them to post through an in-built process. Once a post is made, it is announced on any channel that the bot is currently added to. The bot utilizes a PostgreSQL database to store data, and it is deployed on Heroku.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [Contact](#contact)

## Installation
To get BuffetClearerBot up and running, follow these steps:

### Prerequisites
- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
- [PostgreSQL](https://www.postgresql.org/download/)
- [Python](https://www.python.org/downloads/)

### Steps
1. **Clone the repository**
    ```bash
    git clone [https://github.com/richardleii58/bottest]
    ```

2. **Navigate to the project directory**
    ```bash
    cd buffetclearerbot
    ```

3. **Install the required dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up Heroku**
    ```bash
    heroku create
    heroku addons:create heroku-postgresql:hobby-dev
    ```

5. **Deploy the bot to Heroku**
    ```bash
    git push heroku main
    ```

6. **Set up environment variables**
    Go to your Heroku dashboard, navigate to the settings of your app, and add the following Config Vars:
    - `TOKEN`: Your Telegram bot token.
    - `DATABASE_URL`: Your PostgreSQL database URL (automatically set up by Heroku).
    - `EMAIL_ADDRESS` - Email that sends verification.
    - `EMAIL_PASSWORD`: The password of the email which sends verification.
    - `chat_ids`: chat ids of the channels that you are using for the bot.

7. **Run the worker process**
    ```bash
    heroku ps:scale worker=1
    ```

## Usage
After successfully setting up the bot, you can start using it on Telegram:

1. **Verify Users**
   - Users must verify themselves using the OTP sent to their email.

2. **Post through the In-built Process**
   - Once verified, users can follow the prompts to upload a picture of the food, enter the location, expiry time, and dietary requirements.
   - These posts are then broadcasted to any channel the bot is added to.

### Commands
- `/start`: Start interacting with the bot.
- `/otp`: Verify your user account with an OTP sent to your email.

## Contributing
We welcome contributions from the community. To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request and provide a detailed description of your changes.

## Contact
Richard Lei - [Telegram](@lilleiii) - leirichard58@gmail.com
