import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Secret Key for session management and flash messages
    SECRET_KEY = os.urandom(24)  # Generates a random 24-byte secret key
    SQLALCHEMY_DATABASE_URI = 'mysql://root:abcd@localhost/resource_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
