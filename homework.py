import os
import logging
import requests
import telegram
import time
from http import HTTPStatus
from dotenv import load_dotenv
from telegram import TelegramError
from exceptions import ResponseStatusCodeError, HomeworkStatusNotExist

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 1200
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s, %(levelname)s, %(message)s')
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=None)
logger.addHandler(handler)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info(f'Вам письмо: {message}')
    except telegram.error.TelegramError as error:
        logger.error(f'Сбой отправки сообщения в бот {error}')
        raise TelegramError(f'Сбой отправки сообщения в бот {error}')


def get_api_answer(current_timestamp):
    """Делает запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(ENDPOINT,
                                         headers=HEADERS, params=params)
        if homework_statuses.status_code != HTTPStatus.OK:
            logging.error('Ошибка сервера, код не равен 200')
            raise ResponseStatusCodeError(
                'Неправильный ответ сервера: '
                f'status_code: {homework_statuses.status_code}'
            )
        return homework_statuses.json()
    except requests.RequestException as error:
        logging.error(f'Ошибка запроса сервера. {error}')


def check_response(response):
    """Проверяет ответ API на корректность."""
    if isinstance(response['homeworks'], list):
        return response['homeworks']


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе её статус."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    if homework['status'] not in HOMEWORK_STATUSES:
        logging.error('Какой-то непонятный статус проверки :(')
        raise HomeworkStatusNotExist(
            'Такой статус не существует: '
            f'{homework["status"]}'
        )
    verdict = HOMEWORK_STATUSES[f'{homework_status}']
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Описана основная логика работы программы."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(current_timestamp)
            chk_response = check_response(response)
            print(current_timestamp)
            if len(chk_response) == 0:
                send_message(bot, "Ничего нового нет")
            for i in range(len(chk_response)):
                sts = parse_status(chk_response[i])
                send_message(bot, sts)
            current_timestamp = response['current_date']
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
            logging.critical(message)
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
