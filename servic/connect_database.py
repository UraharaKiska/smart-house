import psycopg2
import sys

sys.path.append('/home/gregorok/mikrohui/server')
from config import *


def database_connect():
    conn = psycopg2.connect(
            host=HOST,
            database=DB_NAME,
            user=LOGIN,
            password=PASS)
    return conn


def database_close_connection(cursor):
    cursor.close()
    
