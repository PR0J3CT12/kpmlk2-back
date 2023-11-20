import os
import yadisk
import dotenv
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = os.path.dirname(__file__)
DOTENV_PATH = os.path.join(PROJECT_ROOT, '.env')
BACKUP_PATH = os.path.join(PROJECT_ROOT, '../backups')
dotenv.load_dotenv(DOTENV_PATH)
YANDEX_ID = os.environ.get("YANDEX_ID")
YANDEX_PASSWORD = os.environ.get("YANDEX_PASSWORD")
YANDEX_TOKEN = os.environ.get("YANDEX_TOKEN")
DB_NAME = os.environ.get("DB_NAME")
DB_USER = os.environ.get("DB_USER")
DB_USER_PASSWORD = os.environ.get("DB_USER_PASSWORD")

now = datetime.now()
day = now.day
month = now.month
year = now.year

BACKUP_FILE_PATH = f'{BACKUP_PATH}/{day}-{month}-{year}.dump'

def upload_file(file):
    try:
        file_name = file.split('/')[-1]
        y_ = yadisk.YaDisk(token=YANDEX_TOKEN)
        y_.upload(file, f'/{file_name}')
        return True
    except Exception as e:
        return False


def get_url_for_token():
    """
    :return: url for yandex oauth
    """
    y_ = yadisk.YaDisk(YANDEX_ID, YANDEX_PASSWORD)
    url_ = y_.get_code_url()
    return url_


def yandex_accept_token(code_):
    """
    token creator
    :param code_: code from yandex accept page
    :return: token or empty string
    """
    y_ = yadisk.YaDisk(YANDEX_ID, YANDEX_PASSWORD)
    try:
        response_ = y_.get_token(code_)
    except yadisk.exceptions.BadRequestError:
        return "Bad code"
    y_.token = response_.access_token
    if y_.check_token():
        return y_.token
    else:
        return "Bad code"


if __name__ == '__main__':
    os.system(f'pg_dump --dbname=postgresql://{DB_USER}:{DB_USER_PASSWORD}@127.0.0.1:5432/{DB_NAME} > {BACKUP_FILE_PATH}')
    backup_file = Path(f'{BACKUP_FILE_PATH}')
    if backup_file.is_file():
        x = upload_file(BACKUP_FILE_PATH)
        print(x)
    else:
        pass