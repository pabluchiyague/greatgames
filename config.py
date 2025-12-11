import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '12345'
    DATABASE = os.path.join(os.getcwd(), 'var', 'greatgames.db')
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB