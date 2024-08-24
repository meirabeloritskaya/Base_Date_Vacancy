
from dotenv import load_dotenv
import os

def config():
    # create a parser
     load_dotenv('.env')
     db = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'port': os.getenv('DB_PORT')
        }
     return db