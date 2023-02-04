[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/desprit/tg-ai-connector/blob/master/README.md)
[![ru](https://img.shields.io/badge/lang-ru-blue.svg)](https://github.com/desprit/tg-ai-connector/blob/master/README.ru.md)

# Установка

Для работы нужен Python 3.10+.

```sh
# Устанавить системные библиотеки
apt install python3.10-dev python3.10-venv
```

```sh
# Создать виртуальное окружение
python3.10 -m venv venv
# Активировать его
source venv/bin/activate
# Устанавить зависимости
pip install -r requirements.txt
```

# Доступные интеграции

1. Dall-E через [Official API](https://beta.openai.com/docs/introduction)
2. ChatGPT через [Official API](https://beta.openai.com/docs/introduction)
3. Midjourney через [Replicate](https://replicate.com/tstramer/midjourney-diffusion)
4. Stable Diffusion через [Replicate](https://replicate.com/tstramer/midjourney-diffusion)

# Использование

## Конфигурация

Пример `config.toml`:

```toml
DEBUG = true

[general]
TEXT_HISTORY_TTL = 300 # как долго хранить сообщения от пользователя, 5 минут по умолчанию
TEXT_HISTORY_SIZE = 10 # сколько сообщений хранить от каждого пользователя

[telegram]
BOT_TOKEN = "ТОКЕН_ОТ_ТЕЛЕГРАМ_БОТА"
ALLOWED_USERS = [123, 234] # опционально, список пользователей, кому можно общаться с ботом
ALLOWED_CHATS = [345, 456] # опционально, список чатов, откуда можно обращаться с ботом

[integrations]
[integrations.openai]
API_KEY = "ТОКЕН_ОТ_OPENAI" # этот токен включает интеграцию с OpenAI
DALLE_COMMAND = "a" # опционально, команда для взаимодействия с сеткой Dall-E, по умолчанию "d"
CHATGPT_COMMAND = "b" # опционально, команда для взаимодействия с ChatGPT, по умолчанию "p"
[integrations.replicate]
API_KEY = "ТОКЕН_ОТ_REPLICATE" # этот токен включает интеграцию с Replicate
MIDJOURNEY_COMMAND = "c" # опционально, команда для взаимодействия с сеткой Midjourney, по умолчанию "m"
STABLE_DIFFUSION_COMMAND = "d" # опционально, команда для взаимодействия с сеткой Stable Diffusion, по умолчанию "s"
```

## Запуск в режиме разработки

```sh
# Запуск бота
make start
# Проверка логов
tail -f log.txt
```

## Запуск на сервере

```sh
# Запуск бота
python -m src.bot &
# Остановка бота
make stop
```

## Полезные команды в Телеграм

```
# Проверить, работает ли бот
/ping
```

Некоторые интеграции могут принимать команду `clear` для очистки истории:

```
# Очистить историю сообщений с OpenAI ChatGPT
/p clear
```

## Возможные ошибки и неполадки

- A request to the Telegram API was unsuccessful. Error code: 409. Description: Conflict: terminated by other getUpdates request; make sure that only one bot instance is running

Скорее всего, бот уже работает. Остановите его командой `make stop`, если это не сработало, вручную найдите процесс и остановите его:

```sh
ps aux | grep "src.bot"
kill -9 <PID>
```
