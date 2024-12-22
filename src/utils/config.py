# src/utils/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DATABASE_PATH = 'data/users.csv'
    UPLOAD_FOLDER = 'data/temp_uploads/'
