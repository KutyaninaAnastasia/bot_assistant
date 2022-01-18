from http import HTTPStatus
import json
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
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info('Отправлено сообщение.')
    except telegram.TelegramError() as error:
        logger.error(f'Сообщение не отправлено. {error}')


def get_api_answer(current_timestamp):
    """Делает запрос к эндпоинту API-сервиса Практикум.Домашка."""
    logger.info('Запрос к эндпоинту API-сервиса')
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    try:
        homework_answer = requests.get(
            ENDPOINT,
            params=params,
            headers=HEADERS
        )
    except requests.exceptions.RequestException as error:
        raise Exception(f'Не верный тип данных {error}.')
    if homework_answer.status_code != HTTPStatus.OK:
        message = f'Эндпоинт {ENDPOINT} недоступен.'
        logger.error(message)
        raise Exception(message)
    logging.info("Получен ответ от сервера.")
    try:
        jhomework_answer = homework_answer.json()
    except json.decoder.JSONDecodError:
        raise Exception('Ответ должен быть преобразован в json ')
    return jhomework_answer


def check_response(response):
    """Проверяет ответ API на корректность."""
    if not isinstance(response, dict):
        raise TypeError('Ответ API не словарь.')
    homework = response['homeworks']
    if not isinstance(homework, list):
        raise TypeError('Ответ API не словарь.')
    if homework is None:
        raise Exception("Задания не обнаружены")
    # if len(homework) == 0:
    #     logger.debug('Нет изменений в статусах домашних работ')
    #     raise ValueError('Нет изменений в статусах домашних работ')

    return homework


def parse_status(homework):
    """Извлекает из информации о домашней работе статус этой работы."""
    if type(homework) == dict:
        if 'status' in homework:
            homework_status = homework.get('status')
        else:
            raise KeyError('Ключа "status" нет в ответе')
        if 'homework_name' in homework:
            homework_name = homework.get('homework_name')
        else:
            raise KeyError('Ключа "homework_name" нет в ответе')
        if homework_status is None:
            raise Exception('Пустое значение status.')
        if homework_name is None:
            raise Exception('Пустое значение homework_name.')
        if homework_status in HOMEWORK_STATUSES:
            verdict = HOMEWORK_STATUSES[homework_status]
            return (f'Изменился статус проверки работы "{homework_name}" :'
                    f' {verdict}')
        else:
            message = 'Статуса домашней работы нет в словаре.'
            logger.error(message)
            raise Exception(message)

    else:
        raise KeyError('Входной параметр не словарь.')


def check_tokens():
    """Проверяет переменные окружения, необходимые для работы программы."""
    if PRACTICUM_TOKEN is None or TELEGRAM_TOKEN is None or \
            TELEGRAM_CHAT_ID is None:
        return False
    return True


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    logger.debug('Бот запущен')
    current_timestamp = int(time.time())
    if not check_tokens():
        message = 'Проверьте обязательные переменные окружения.'
        logger.critical(message)
        raise SystemExit(message)
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if homework is not None:
                if len(response) > 0:
                    for hw in homework:
                        status = parse_status(hw)
                        if status is not None:
                            send_message(bot, status)
                            logger.info(
                                'Сообщение о статусе работы отправлено')
                else:
                    logger.debug('Нет изменений в статусах домашних работ')
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
