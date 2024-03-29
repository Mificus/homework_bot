import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exception import SendMessageError, GetApiAnswerError
from exception import UnavailableEndpoint, ResponseDateError

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s, %(name)s %(levelname)s %(message)s'
)
handler.setFormatter(formatter)


def check_tokens():
    """Проверяем доступность переменных окружения."""
    variables = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(variables)


def send_message(bot, message):
    """Отправляем сообщение в телеграм чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'send message {message}')
    except telegram.error.TelegramError as error:
        text = f'Ошибка отправки сообщения, {error}'
        logger.error(text)
        raise SendMessageError(text)


def get_api_answer(timestamp):
    """Делаем запрос к эндпойнту."""
    try:
        payload = {'from_date': timestamp}
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        logger.debug('Запрос к Эндпойнту')
        if response.status_code != HTTPStatus.OK:
            text = f'Код запроса не 200 и равен {response.status_code}'
            raise GetApiAnswerError(text)
    except requests.exceptions.RequestException as error:
        text = f'Эндпойнт недоступен. Ошибка: {error}'
        raise UnavailableEndpoint(text)
    try:
        response_content = response.json()
    except ValueError:
        raise ResponseDateError
    return response_content


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('Ответ API-сервера содержит неверный тип данных.')
    if 'homeworks' not in response:
        raise KeyError('Ответ от API не содержит ключ "homeworks".')
    homeworks = response['homeworks']
    if not isinstance(homeworks, list):
        raise TypeError('В ответ API-сервера содержит неверный тип данных.')
    logger.debug('Ответ от API-сервера корректен')
    return response.get('homeworks')


def parse_status(homework):
    """.
    Извлекаем из информации о конкретной
    домашней работе статус этой работы.
    """
    homework_name = homework.get('homework_name')
    if homework_name is None:
        text = 'В ответе API нет ключа homework_name'
        raise KeyError(text)
    homework_status = homework.get('status')
    if homework_status is None:
        text = 'В ответе API нет ключа homework_status'
        logger.error(text)
        raise KeyError(text)
    verdict = HOMEWORK_VERDICTS.get(homework_status)
    if verdict is None:
        text = 'Неизвестный статус'
        logger.error(text)
        raise KeyError(text)
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    last_message = ''
    if not check_tokens():
        text = 'Переменные окружения недоступны'
        logger.critical(text)
        sys.exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time()) - RETRY_PERIOD

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if len(homeworks) > 0:
                homework_status = parse_status(homeworks[0])
                if homework_status is not None:
                    send_message(bot, homework_status)
            else:
                logger.debug('Новый статус не обнаружен')
        except SendMessageError as error:
            logger.error(error)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if message != last_message:
                send_message(bot, message)
                last_message = message
            logger.error(message)
        finally:
            timestamp = int(time.time())
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
