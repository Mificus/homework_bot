import logging
import os
import time
import json
import requests
import telegram
from dotenv import load_dotenv
from pprint import pprint
from exception import TokensError

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s, %(name)s %(levelname)s %(message)s'
)
handler.setFormatter(formatter)

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
payload = {'from_date': 0}
# Делаем GET-запрос к эндпоинту url с заголовком headers и параметрами params
homework_statuses = requests.get(ENDPOINT, headers=HEADERS, params=payload)

# Печатаем ответ API в формате JSON
prom = homework_statuses.json()
homeworks = prom.get('homeworks')
print(homeworks[0]['status'])
print(homeworks)
# А можно ответ в формате JSON привести к типам данных Python и напечатать и его
# pprint(homework_statuses.json()['homeworks'][0])

