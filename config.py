import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    DEBUG = True
    SECRET_KEY = 'Pa$$w0rd'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:Pa$$w0rd@localhost/veterinaria'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de correo
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'formessaging87@gmail.com'
    MAIL_PASSWORD = 'uejmlnfoguxdjpac'
