[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/desprit/tg-ai-connector/blob/master/README.md)
[![ru](https://img.shields.io/badge/lang-ru-blue.svg)](https://github.com/desprit/tg-ai-connector/blob/master/README.ru.md)

# Установка

## Докер

https://hub.docker.com/repository/docker/desprit/tg-ai-connector/general

```sh
# Создайте файл, в котором будут чаты и пользователи, которым разрешено общаться с ботом
touch /path/to/whitelist.txt

# Если у вас Linux
docker run -d --rm \
   -v /path/to/config.toml:/app/bot/config.toml \
   -v /path/to/whitelist.txt:/app/bot/whitelist.txt \
   desprit/tg-ai-connector:1.0.0

# Если у вас MacOS M1
docker run -d --rm \
   --platform linux/amd64 \
   -v /path/to/config.toml:/app/bot/config.toml \
   -v /path/to/whitelist.txt:/app/bot/whitelist.txt \
   desprit/tg-ai-connector:1.0.0
```

Если нужно, используйте лог файл с хоста и пробросьте его в контейнер:

```sh
# Создайте лог-файл
touch /path/to/log.txt

docker run \
   -v /path/to/config.toml:/app/bot/config.toml \
   -v /path/to/whitelist.txt:/app/bot/whitelist.txt \
   -v /path/to/log.txt:/app/bot/log.txt \
   desprit/tg-ai-connector:1.0.0

tail -f /path/to/log.txt
```

## Ручками

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
   - Text Completion
2. Replicate через [Replicate](https://replicate.com)
   - Midjourney
   - Stable Diffusion
   - Other networks

Relicate предлагает множество разных сеток. Изначально я использовал только генерацию картинок, но недавно обнаружил [конвертацию аудио в текст](https://replicate.com/openai/whisper/api). Так как нужно отправить в эту сетку аудио, самый простой способ - это использовать "reply" в чате Телеграма. Выделяем аудио сообщение, отвечаем на него командой `/a` (или другой командой, которую вы выбрали для интеграции с `openai/whisper`), можно также опционально указать язык распознавания, например `/a de`.

Возможно, нужно будет также изменить настройки приватности бота:
https://stackoverflow.com/questions/50204633/allow-bot-to-access-telegram-group-messages

# Использование

## Авторизация

Вы можете управлять списком разрешенных пользователей и чатов, записывая их идентификаторы в конфиг. Вы также можете добавить в конфиг admin_id (идентификатор администратора) и дальше пользоваться командами бота:

```sh
/whitelist user_id
/whitelist username
/whitelist chat_id
/blacklist user_id
/blacklist username
/blacklist chat_id
```

## Конфигурация

Пример `config.toml`:

```toml
debug = true

[general]
text_history_ttl = 300 # опционально, как долго хранить сообщения от пользователя, 5 минут по умолчанию
text_history_size = 10 # опционально, сколько сообщений хранить от каждого пользователя, по умолчанию 10

[telegram]
bot_token = "ТОКЕН_ОТ_ТЕЛЕГРАМ_БОТА"
admin_id = 111 # опционально, идентификатор администратора, которому можно запрещать и разрешать доступ пользователям и чатам
allowed_users = [123, 234] # опционально, список пользователей, кому можно общаться с ботом
allowed_chats = [345, 456] # опционально, список чатов, откуда можно обращаться с ботом

[integrations]

[integrations.openai]
api_key = "OPEN_AI_TOKEN" # этот токен включает интеграцию с OpenAI
max_tokens = 1000 # максимальное количество токенов, возвращаемое текстовыми моделями OpenAI, 500 по умолчанию
[[integrations.openai.networks]]
name = "completion"
version = "text-davinci-003"
command = "t" # Telegram команда для взаимодействия с Text Completion
[[integrations.openai.networks]]
name = "chat"
version = "gpt-4"
command = "c" # Telegram команда для взаимодействия с ChatGPT
[[integrations.openai.networks]]
name = "image"
version = "dalle"
command = "d" # Telegram команда для взаимодействия с сеткой Dall-E

[integrations.replicate]
api_key = "REPLICATE_TOKEN" # этот токен включает интеграцию с Replicate
[[integrations.replicate.networks]]
name = "tstramer/midjourney-diffusion"
version = "436b051ebd8f68d23e83d22de5e198e0995357afef113768c20f0b6fcef23c8b"
command = "m" # Telegram команда для взаимодействия с сеткой Midjourney
type = "image"
[[integrations.replicate.networks]]
name = "stability-ai/stable-diffusion"
version = "f178fa7a1ae43a9a9af01b833b9d2ecf97b1bcb0acfd2b1c1c1c1c1c1c1c1c1c"
command = "s" # Telegram команда для взаимодействия с сеткой Stable Diffusion
type = "image"
[[integrations.replicate.networks]]
name = "cjwbw/anything-v3.0"
version = "f410ed4c6a0c3bf8b76747860b3a3c9e4c8b5a827a16eac9dd5ad9642edce9a2"
command = "anything" # Telegram команда для взаимодействия с сеткой cjwbw/anything-v3.0
type = "image"
[[integrations.replicate.networks]]
name = "cjwbw/portraitplus"
version = "629a9fe82c7979c1dab323aedac2c03adaae2e1aecf6be278a51fde0245e20a4"
command = "portraitplus" # Telegram команда для взаимодействия с сеткой cjwbw/portraitplus
type = "image"
[[integrations.replicate.networks]]
name = "openai/whisper"
version = "e39e354773466b955265e969568deb7da217804d8e771ea8c9cd0cef6591f8bc" # Telegram команда для взаимодействия с сеткой openai/whisper для конвертации аудио в текст
type = "audio"
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

ChatGPT и Text Completion хранит историю запросов, ее можно очистить вручную используя команду `clear`:

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
