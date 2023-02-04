[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
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

1. OpenAI через [Official API](https://beta.openai.com/docs/introduction)
   - Dall-E
   - ChatGPT
2. Replicate через [Replicate](https://replicate.com)
   - Midjourney
   - Stable Diffusion
   - Other networks

# Использование

## Конфигурация

Пример `config.toml`:

```toml
debug = true

[general]
text_history_ttl = 300 # опционально, как долго хранить сообщения от пользователя, 5 минут по умолчанию
text_history_size = 10 # опционально, сколько сообщений хранить от каждого пользователя, по умолчанию 10

[telegram]
bot_token = "ТОКЕН_ОТ_ТЕЛЕГРАМ_БОТА"
allowed_users = [123, 234] # опционально, список пользователей, кому можно общаться с ботом
allowed_chats = [345, 456] # опционально, список чатов, откуда можно обращаться с ботом

[integrations]

[integrations.openai]
api_key = "OPEN_AI_TOKEN" # этот токен включает интеграцию с OpenAI
[[integrations.openai.networks]]
name = "chatgpt"
command = "p" # Telegram команда для взаимодействия с ChatGPT
[[integrations.openai.networks]]
name = "dalle"
command = "d" # Telegram команда для взаимодействия с сеткой Dall-E

[integrations.replicate]
api_key = "REPLICATE_TOKEN" # этот токен включает интеграцию с Replicate
[[integrations.replicate.networks]]
name = "tstramer/midjourney-diffusion"
version = "436b051ebd8f68d23e83d22de5e198e0995357afef113768c20f0b6fcef23c8b"
command = "m" # Telegram команда для взаимодействия с сеткой Midjourney
[[integrations.replicate.networks]]
name = "stability-ai/stable-diffusion"
version = "f178fa7a1ae43a9a9af01b833b9d2ecf97b1bcb0acfd2b1c1c1c1c1c1c1c1c1c"
command = "s" # Telegram команда для взаимодействия с сеткой Stable Diffusion
[[integrations.replicate.networks]]
name = "cjwbw/anything-v3.0"
version = "f410ed4c6a0c3bf8b76747860b3a3c9e4c8b5a827a16eac9dd5ad9642edce9a2"
command = "anything" # Telegram команда для взаимодействия с сеткой cjwbw/anything-v3.0
[[integrations.replicate.networks]]
name = "cjwbw/portraitplus"
version = "629a9fe82c7979c1dab323aedac2c03adaae2e1aecf6be278a51fde0245e20a4"
command = "portraitplus" # Telegram команда для взаимодействия с сеткой cjwbw/portraitplus
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
# Показать список доступных команд
/help
```

ChatGPT хранит историю запросов, ее можно очистить вручную используя команду `clear`:

```
/p clear
```

## Возможные ошибки и неполадки

- A request to the Telegram API was unsuccessful. Error code: 409. Description: Conflict: terminated by other getUpdates request; make sure that only one bot instance is running

Скорее всего, бот уже работает. Остановите его командой `make stop`, если это не сработало, вручную найдите процесс и остановите его:

```sh
ps aux | grep "src.bot"
kill -9 <PID>
```
