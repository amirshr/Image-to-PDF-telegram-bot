import sqlite3
import os
from dotenv import load_dotenv
from pyrogram import Client
import time

load_dotenv()

os.environ['TZ'] = 'Iran'
time.tzset()

t = time.strftime('%X %x')

dpx_token = os.getenv('DROPBOX_TOKEN')
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
phonenumber = os.getenv("PHONENUMBER")


def add_user_to_db(message):
    print(message.date)
    conn = sqlite3.connect('ImgPdfUsers.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                 (full_name text, username text, user_id text UNIQUE,date text)''')

    global rows_count
    rows = cursor.execute('SELECT COUNT(*) FROM users')
    rows_count = rows.fetchall()[0][0]

    user = (message.chat.full_name, message.chat.username, message.chat.id, message.date)
    try:
        cursor.execute("INSERT INTO users VALUES (?,?,?,?)", user)
        conn.commit()
        conn.close()
        return True

    except Exception as e:
        conn.close()
        print(e)
        return False


def upload_database():
    app = Client("MyAcc", api_id, api_hash, phone_number=phonenumber)
    app.start()
    for chat in app.iter_dialogs():
        if chat.chat.title == 'ImageToPdf Users':
            channel_id = chat.chat.id
            try:
                app.send_document(channel_id, 'BotUsers.db', caption=str(rows_count))
                print('db sended to channel')
            except Exception as e:
                print(e)
                pass
    app.stop()
