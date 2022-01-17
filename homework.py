import logging
import os
import time

from dotenv import load_dotenv
import requests
import telegram

load_dotenv()

logging.basicConfig(
    level=logging.DEBUG,
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

PRACTICUM_TOKEN = os.getenv('PRAKTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info('Отправлено сообщение.')
    except Exception as error:
        logger.error(f'Сообщение не отправлено. {error}')


def get_api_answer(current_timestamp):
    logger.info('Запрос к эндпоинту API-сервиса')
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    try:
        homework_answer = requests.get(
            ENDPOINT,
            params=params,
            headers=HEADERS
        )
    except TypeError as error:
        raise Exception(f'Не верный тип данных {error}.')
    if homework_answer.status_code != 200:
        message = f'Эндпоинт {ENDPOINT} недоступен.'
        logger.error(message)
        raise Exception(message)
    logging.info("Получен ответ от сервера.")
    return homework_answer.json()


def check_response(response):
    if not isinstance(response, dict):
        raise TypeError('Ответ API не словарь.')
    hw = ['homeworks'][0]
    if hw not in response:
        raise Exception('В ответе API нет домашней работы.')
    homework = response.get('homeworks')[0]
    # logger.info(type(homework))
    return homework


def parse_status(homework):
    if type(homework) == dict:
        homework_name = homework['homework_name']
        homework_status = homework['status']
        if homework_status is None:
            raise Exception('Пустое значение status.')
        if homework_name is None:
            raise Exception('Пустое значение homework_name.')
        if homework_status not in HOMEWORK_STATUSES:
            message = f'Статуса домашней работы нет в словаре.'
            logger.error(message)
            raise Exception(message)
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}" : {verdict}'
    else:
        raise KeyError('Входной параметр не словарь.')


def check_tokens():
    if PRACTICUM_TOKEN is None or TELEGRAM_TOKEN is None or \
            TELEGRAM_CHAT_ID is None:
        return False
    return True


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    logger.debug('Бот запущен')
    current_timestamp = 0
    if check_tokens() is False:
        message = 'Проверьте обязательные переменные окружения.'
        logger.critical(message)
        raise SystemExit(message)
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if homework is not None:
                status = parse_status(homework)
                if status is not None:
                    send_message(bot, status)
                    logger.info('Сообщение о статусе работы отправлено')
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
