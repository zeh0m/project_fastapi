from decouple import config



KEY = config('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

FASTAPI_TARGET = config('MY_URL_FASTAPI')


ENGINE = config('DB_ENGINE')
NAME = config('DB_NAME')
USER = config('DB_USER')
PASSWORD = config('DB_PASSWORD')
HOST = config('DB_HOST')
PORT = config('DB_PORT')

SUPERUSER = config('SUPERUSER')
PASSWORD_USER = config('PASSWORD_USER')