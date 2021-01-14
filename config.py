import os
from dotenv import load_dotenv
load_dotenv()


def getKeys():
    # Current keys we are using in the system
    key_names = []

    for x in os.listdir('keys'):
        if "pub" not in x:
            key_names.append(x.strip(".key"))


    # This will simply store the keys in a python dict
    # for easier access
    keys = []

    # Get all keys:
    for x in key_names:

        key_id = x

        pubKey = open('keys/' + x + '.key.pub', 'r').read()
        pubKey = "\n".join([l.lstrip() for l in pubKey.split("\n")])

        privKey = open('keys/' + x + '.key', 'r').read()
        privKey = "\n".join([l.lstrip() for l in privKey.split("\n")])

        keys.append({
            "id": key_id,
            "pubKey": pubKey,
            "privKey": privKey
        })
    return keys



class Config(object):
    DEBUG = False
    TESTING = False

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME")

    STRIPE_PK = os.getenv("STRIPE_PK")
    STRIPE_SK = os.getenv("STRIPE_SK")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

    # Main App Config:
    APP_VERSION='0.0.1'
    APP_NAME = 'Python JWT Auth'
    APP_LOGO_URL = 'https://placehold.it/350x150'
    APP_URL = 'https://localhost/'
    API_ENDPOINT = 'https://api.localhost/'
    JWT_HEADER_NAME = 'python-auth'
    JWT_HEADER_TYPE = 'Bearer'
    JWT_ALGORITHM = 'RS256'
    JWT_AUDIENCE = 'python-jwt-auth'
    JWT_ISSUER = 'localhost'
    UPLOAD_FOLDER = 'uploads'

    # Mailer Configuration:
    MAILER_NAME = 'Python JWT Auth'
    MAILER_ADDRESS = 'python@example.com'
    MAILGUN_MESSAGES_ENDPOINT = 'https://api.mailgun.net/v3/<YOUR_DOMAIN>/messages'
    MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")

    DISABLE_SIGNUP = False
    REQUIRE_VERIFIED_EMAIL = False

    MAX_CONTENT_LENGTH = 500 * 1024 * 1024

    # Keys:
    JWT_KEYS = getKeys()


class ProductionConfig(Config):
    S3_SERVER = "production"
    S3_REGION = os.getenv("S3_REGION_PROD")
    S3_ENDPOINT = os.getenv("S3_ENDPOINT_PROD")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY_PROD")
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY_PROD")


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    S3_SERVER = "dev"
    S3_REGION = os.getenv("S3_REGION_DEV")
    S3_ENDPOINT = os.getenv("S3_ENDPOINT_DEV")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY_DEV")
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY_DEV")
    


