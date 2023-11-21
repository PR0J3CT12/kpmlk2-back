import os
import yadisk
import dotenv
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = os.path.dirname(__file__)
DOTENV_PATH = os.path.join(PROJECT_ROOT, '.env')
BACKUP_PATH = os.path.join(PROJECT_ROOT, '../backups')
dotenv.load_dotenv(DOTENV_PATH)
MEDIA_PATH = os.path.join(PROJECT_ROOT, 'media')
YANDEX_ID = os.environ.get("YANDEX_ID")
YANDEX_PASSWORD = os.environ.get("YANDEX_PASSWORD")
YANDEX_TOKEN = os.environ.get("YANDEX_TOKEN")

now = datetime.now()
day = now.day
month = now.month
year = now.year

BACKUP_FILE_PATH = f'{BACKUP_PATH}/{day}-{month}-{year}.tar.gz'
BACKUP_LOG_FILE_PATH = f'{BACKUP_PATH}/logs.txt'


def upload_file(file):
    try:
        file_name = file.split('/')[-1]
        y_ = yadisk.YaDisk(token=YANDEX_TOKEN)
        y_.upload(file, f'/backups/{file_name}')
        return {'state': 'success'}
    except Exception as e:
        return {'state': 'error', 'message': str(e)}


def main():
    os.system(f'tar -zcf {BACKUP_FILE_PATH} {MEDIA_PATH}')
    backup_file = Path(f'{BACKUP_FILE_PATH}')
    if backup_file.is_file():
        with open(BACKUP_LOG_FILE_PATH, 'a') as f:
            f.write(f'{datetime.now()} | backup media V\n')
        #uploaded = upload_file(BACKUP_FILE_PATH)
        #if uploaded['state'] == 'success':
        #    with open(BACKUP_LOG_FILE_PATH, 'a') as f:
        #        f.write(f'V\n')
        #else:
        #    with open(BACKUP_LOG_FILE_PATH, 'a') as f:
        #        f.write(f'X | {uploaded["message"]}\n')
    else:
        with open(BACKUP_LOG_FILE_PATH, 'a') as f:
            f.write(f'{datetime.now()} | backup media X\n')


if __name__ == '__main__':
    main()