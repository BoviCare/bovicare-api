import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # RAG Service Configuration
    RAG_SERVICE_URL = os.getenv('RAG_SERVICE_URL', 'http://localhost:8000')
    RAG_SERVICE_TIMEOUT = int(os.getenv('RAG_SERVICE_TIMEOUT', '180'))  # 180 seconds (3 minutes)