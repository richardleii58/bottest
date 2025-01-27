import json
import requests
import time
import urllib.parse
import datetime
import os # to access files from your computer. necessary to get the .env file
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv # to use the .env file

##import keep_alive

# TOKEN = os.environ['TOKEN']
# URL = f"https://api.telegram.org/bot{TOKEN}/"
# DATABASE_URL = os.environ['DATABASE_URL'] 

DATABASE_URL = os.environ['DATABASE_URL']
# load_dotenv("./.env")
# DATABASE_URL = os.getenv("DATABASE_URL")
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

# cursor.execute("DROP TABLE IF EXISTS verified_users;") # used to delete table (if there are changes lol)

# Create tables if they don't exist
cursor.execute('''
     CREATE TABLE IF NOT EXISTS buffet (
        id SERIAL PRIMARY KEY,
        file_id TEXT not null,
        location TEXT not null,
        expiry TEXT not null,
        diet TEXT not null, 
        info TEXT
    );
''') # triple ' lets you enter multiline

cursor.execute('''
     CREATE TABLE IF NOT EXISTS verified_users (
        user_id BIGINT PRIMARY KEY
    );
''') # triple ' lets you enter multiline

conn.commit() # this line saves whatever you did to the database, basically

conn.close()


def executeSQL(sqlStatement):
    DATABASE_URL = os.environ['DATABASE_URL'] 
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
    cursor.execute(sqlStatement)
    conn.commit() # this line saves whatever you did to the database, basically

    conn.close()


def getVerifiedUserIDs():
    DATABASE_URL = os.environ['DATABASE_URL'] 
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
    cursor.execute("select * from verified_users;")
    result = cursor.fetchall()
    conn.commit() # this line saves whatever you did to the database, basically

    conn.close()

    # result is a list of tuples, with one element in each tuple
    # change result to a list of strings/numbers instead
    new_result = []
    for tup in result:
        new_result.append(tup[0])

    return new_result

def addVerifiedUser(user_id):
    sqlStatement = f"insert into verified_users values ({user_id})"
    executeSQL(sqlStatement)

def deleteVerifiedUser():
    sqlStatement = "DELETE FROM verified_users"
    executeSQL(sqlStatement)
    print(f"Verified users has been deleted.")

