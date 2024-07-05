import json
import requests
import time
import urllib.parse
import datetime
import os
import psycopg2
from urllib.parse import urlparse
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
cursor = conn.cursor()

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
    if 'photo' in x['message']:
        file_id = x['message']['photo'][0]['file_id']
        if 'caption' in x['message']:
            cap = x['message']['caption']
        else:
            cap = ''
        if cap[:9] == 'Broadcast':
            send_broadcast(file_id, cap[9:])
            send_message("Announcement Sent", -758984080)
    msg = x['message']['text']
    if msg[:9] == 'Broadcast':
        to_send = msg[9:]
        send_broadcast(None, to_send)
        send_message2("Announcement Sent", -758984080)
    if msg[:3] == 'New':
        items = msg.split(';')
        add_question(f"Q{len(fetch_all_questions()) + 1}", [], items[1], items[2])
        send_message2(f'Qn added num {len(fetch_all_questions())}', x['message']['chat']['id'])
    elif msg == 'List everything':
        send_message2(fetch_all_questions(), x['message']['chat']['id'])
    elif msg[:6] == 'AddKey':
        msg = msg.upper()
        items = msg.split(';')
        lst = items[2].split(',')
        cursor.execute('''
            UPDATE qns SET keywords = array_cat(keywords, %s)
            WHERE question_number = %s;
        ''', (lst, items[1]))
        conn.commit()
        send_message('Keyword added', x['message']['chat']['id'])
    elif msg[:6] == 'AddCat':
        lst = msg.split(';')
        qn = lst[1]
        cat = lst[2]
        cursor.execute('''
            INSERT INTO categories (category_name, question_number)
            VALUES (%s, %s);
        ''', (cat, qn))
        conn.commit()
        send_message2(f'Question {qn} added to category {cat}', -758984080)
    elif msg[:3] == 'Del':
        items = msg.split(';')
        cursor.execute('DELETE FROM qns WHERE question_number = %s;', (items[1],))
        conn.commit()
        send_message('QnA deleted', x['message']['chat']['id'])
    elif 'reply_to_message' in x['message']:
        reply = x['message']['reply_to_message']['text']
        if reply[:3].upper() == 'NEW' and msg[:5].upper() == 'REPLY':
            reply = reply.split(';;')
            chat = reply[1]
            qnn = reply[0].split('from')[0]
            qn_list = []
            for item in fetch_all_questions():
                for word in item['keywords']:
                    if word.upper() in msg.upper():
                        qn_list.append(item['question_number'])
            qn_list = list(set(qn_list))
            msg_send = ''
            qn_list.sort()
            for qnnn in qn_list:
                msg_send += qnnn + ':' + db['qns'][qnnn]['A'] + '\n\n'
            if not qn_list:
                send_message2('Sorry, I don\'t know the answer.', chat)
            else:
                send_message2(msg_send, chat)

def echo_all(updates):
    for update in updates["result"]:
        try:
            text, chat = get_last_chat_id_and_text(updates)
            if chat == -758984080:
                admin(update)
            else:
                cursor.execute('''
                    SELECT COUNT(*) FROM users WHERE chat_id = %s;
                ''', (chat,))
                exists = cursor.fetchone()[0]
                if exists == 0:
                    cursor.execute('''
                        INSERT INTO users (chat_id, first_name, date_joined)
                        VALUES (%s, %s, %s);
                    ''', (chat, update['message']['chat']['first_name'], datetime.date.today()))
                    conn.commit()
                if text[:5].upper() == 'REPLY':
                    qn_list = []
                    for item in fetch_all_questions():
                        for word in item['keywords']:
                            if word.upper() in text.upper():
                                qn_list.append(item['question_number'])
                    qn_list = list(set(qn_list))
                    qn_list.sort()
                    msg_send = ''
                    for qnnn in qn_list:
                        msg_send += qnnn + ':' + item['answer'] + '\n\n'
                    if not qn_list:
                        send_message2('Sorry, I don\'t know the answer.', chat)
                    else:
                        send_message2(msg_send, chat)
                elif text.upper() == 'NEW' or text.upper() == 'HELLO':
                    send_message2(f'Hello {update["message"]["chat"]["first_name"]}! How can I help you today?', chat)
                else:
                    qn_list = []
                    for item in fetch_all_questions():
                        for word in item['keywords']:
                            if word.upper() in text.upper():
                                qn_list.append(item['question_number'])
                    qn_list = list(set(qn_list))
                    qn_list.sort()
                    msg_send = ''
                    for qnnn in qn_list:
                        msg_send += qnnn + ':' + item['answer'] + '\n\n'
                    if not qn_list:
                        send_message2('Sorry, I don\'t know the answer.', chat)
                    else:
                        send_message2(msg_send, chat)
        except Exception as e:
            print(e)

def main():
    ##keep_alive.keep_alive()
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if "result" in updates and len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all(updates)
        time.sleep(0.5)

if __name__ == '__main__':
    main()
