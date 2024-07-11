import json
import requests
import time
import urllib.parse
import datetime
import os
import psycopg2
from urllib.parse import urlparse
##import keep_alive

# TOKEN = os.environ['TOKEN']
# URL = f"https://api.telegram.org/bot{TOKEN}/"

# DATABASE_URL = os.environ['DATABASE_URL'] 
DATABASE_URL = "insert url directly here (for testing)"
url = urlparse(DATABASE_URL) 

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)
print(conn)
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
cursor.execute('''create table course 
                    (CID	char(8)	not null,
                    CName varchar(15) not null,
                    CONSTRAINT course_pk primary key (CID)
                    );
                ''') # triple ' lets you enter multiline

conn.commit() # this line saves whatever you did to the database, basically

conn.close()
