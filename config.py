import os

from dotenv import load_dotenv

load_dotenv()

LOGIN = os.getenv('LOGIN')
PASS = os.getenv('PASS')
DB_NAME = os.getenv('DB_NAME')
HOST = os.getenv('HOST')
PORT = os.getenv('PORT')
API_TOKEN_BOT = os.getenv('API_TOKEN_BOT')
RABBIT_USER = os.getenv('RABBIT_USER')
RABBIT_PASS = os.getenv('RABBIT_PASS')