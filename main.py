# import json
# import requests
# import time
# import urllib.parse
# import datetime
# import os
# import psycopg2
# from urllib.parse import urlparse
# ##import keep_alive

# TOKEN = os.environ['TOKEN']
# URL = f"https://api.telegram.org/bot{TOKEN}/"

# DATABASE_URL = os.environ['DATABASE_URL']
# url = urlparse(DATABASE_URL)
# conn = psycopg2.connect(
#     database=url.path[1:],
#     user=url.username,
#     password=url.password,
#     host=url.hostname,
#     port=url.port
# )
# conn.set_session(readonly=False)  # Ensure the connection is not read-only
# cursor = conn.cursor()

# # Create tables if they don't exist
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS users (
#         id SERIAL PRIMARY KEY,
#         chat_id BIGINT UNIQUE,
#         first_name TEXT,
#         date_joined DATE
#     );
# ''')
# conn.commit()

# def get_url(url):
#     response = requests.get(url)
#     content = response.content.decode("utf8")
#     return content

# def get_json_from_url(url):
#     content = get_url(url)
#     js = json.loads(content)
#     return js

# def get_updates(offset=None):
#     url = URL + "getUpdates?timeout=100"
#     if offset:
#         url += f"&offset={offset}"
#     js = get_json_from_url(url)
#     return js

# def get_last_chat_id_and_text(updates):
#     num_updates = len(updates["result"])
#     last_update = num_updates - 1
#     text = updates["result"][last_update]["message"]["text"]
#     chat_id = updates["result"][last_update]["message"]["chat"]["id"]
#     return text, chat_id

# def send_message(text, chat_id):
#     text = urllib.parse.quote_plus(text)
#     url = URL + f"sendMessage?text={text}&chat_id={chat_id}&parse_mode=MarkdownV2"
#     get_url(url)

# def send_message2(text, chat_id):
#     text = urllib.parse.quote_plus(text)
#     url = URL + f"sendMessage?text={text}&chat_id={chat_id}"
#     get_url(url)

# def send_photo(photo, chat_id, cap):
#     photo = urllib.parse.quote_plus(photo)
#     url = URL + f"sendPhoto?photo={photo}&chat_id={chat_id}&caption={cap}"
#     get_url(url)

# def get_last_update_id(updates):
#     update_ids = []
#     for update in updates["result"]:
#         update_ids.append(int(update["update_id"]))
#     return max(update_ids)

# def admin(x):
#     print("hello")
    
# def main():
#     print("hello") 
    
#     while True:
#         i = 1


# if __name__ == '__main__':
#     main()
