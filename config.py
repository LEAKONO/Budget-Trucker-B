import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'bY7Gm2P!qv4Z$kZ1s8JtXo3fNm9Hc2W#Jb5C6Qs7DpE')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///site.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
