# Бот-ассистент.
Telegram-бот, который обращается к API сервиса Практикум.Домашка и узнаёт статус домашней работы: взята ли она в ревью, проверена, а если проверена — то принял её ревьюер или вернул на доработку.

Используемые технологии
Python 3.8
python-telegram-bot 12.7

### Для работы боту требуется файл .env со следующими переменными окружения:
PRAKTIKUM_TOKEN - Токен, полученный на платформе Яндекс.Практикум
TELEGRAM_TOKEN - Токен вашего бота, полученный через @BotFather
TELEGRAM_CHAT_ID - Ваш Chat_id

## Что делает бот.

- Функция check_tokens(): проверяет доступность переменных окружения, которые необходимы для работы программы.
- Функция get_api_answer(): раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы.  В случае успешного запроса функция возвращает ответ API, преобразовав его из формата JSON к типам данных Python.
- Функция check_response(): При обновлении статуса проверяет ответ API на корректность. В качестве параметра функция получает ответ API, приведенный к типам данных Python. Если ответ API соответствует ожиданиям,возвращает список домашних работ (он может быть и пустым), доступный в ответе API по ключу 'homeworks'
- Функция parse_status(): извлекает из информации о конкретной домашней работе статус этой работы. В качестве параметра функция получает только один элемент из списка домашних работ. В случае успеха, функция возвращает подготовленную для отправки в Telegram строку, содержащую один из вердиктов словаря HOMEWORK_STATUSES.
```
HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
```
- Функция send_message(): отправляет сообщение в Telegram чат, определяемый переменной окружения TELEGRAM_CHAT_ID. Принимает на вход два параметра: экземпляр класса Bot и строку с текстом сообщения.
- Логирует свою работу и сообщает о важных проблемах сообщением в Telegram.

### Логирование.

Каждое сообщение в журнале логов состоит из: 
- даты и времени события,
- уровня важности события,
- описания события. Например:
```
2022-05-04 15:34:45,150 [ERROR] Сбой в работе программы: Эндпоинт https://practicum.yandex.ru/api/user_api/homework_statuses/111 недоступен. Код ответа API: 404
2021-05-04 15:34:45,355 [INFO] Бот отправил сообщение "Сбой в работе программы: Эндпоинт [https://practicum.yandex.ru/api/user_api/homework_statuses/](https://practicum.yandex.ru/api/user_api/homework_statuses/) недоступен. Код ответа API: 404"
```
Логируемые события:
* отсутствие обязательных переменных окружения во время запуска бота (уровень CRITICAL).
* удачная отправка любого сообщения в Telegram (уровень INFO);
* сбой при отправке сообщения в Telegram (уровень ERROR);
* недоступность эндпоинта https://practicum.yandex.ru/api/user_api/homework_statuses/ (уровень ERROR);
* любые другие сбои при запросе к эндпоинту (уровень ERROR);
* отсутствие ожидаемых ключей в ответе API (уровень ERROR);
* недокументированный статус домашней работы, обнаруженный в ответе API (уровень ERROR);
* отсутствие в ответе новых статусов (уровень DEBUG).

События уровня ERROR не только логируются, но и пересылается информация о них в Telegram.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/KutyaninaAnastasia/bot_assistant.git
```

```
cd bot_assistant
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
