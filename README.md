[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/desprit/tg-ai-connector/blob/master/README.md)
[![ru](https://img.shields.io/badge/lang-ru-blue.svg)](https://github.com/desprit/tg-ai-connector/blob/master/README.ru.md)

# Installation

## Docker

https://hub.docker.com/repository/docker/desprit/tg-ai-connector/general

```sh
# Create file to store whitelisted chats and users
touch /path/to/whitelist.txt

# If you're on Linux
docker run -d --rm \
   -v /path/to/config.toml:/app/bot/config.toml \
   -v /path/to/whitelist.txt:/app/bot/whitelist.txt \
   desprit/tg-ai-connector:1.0.0

# If you're on MacOS M1
docker run -d --rm \
   --platform linux/amd64 \
   -v /path/to/config.toml:/app/bot/config.toml \
   -v /path/to/whitelist.txt:/app/bot/whitelist.txt \
   desprit/tg-ai-connector:1.0.0
```

Map log file from the host to the container if needed:

```sh
# Create log file
touch /path/to/log.txt

docker run \
   -v /path/to/config.toml:/app/bot/config.toml \
   -v /path/to/whitelist.txt:/app/bot/whitelist.txt \
   -v /path/to/log.txt:/app/bot/log.txt \
   desprit/tg-ai-connector:1.0.0

tail -f /path/to/log.txt
```

## Manual

Python 3.10+ is required.

```sh
# Install system packages
apt install python3.10-dev python3.10-venv
```

```sh
# Create Virtual environment
python3.10 -m venv venv
# Activate it
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt
```

# Available integrations

1. OpenAI through [Official API](https://beta.openai.com/docs/introduction)
   - Dall-E
   - ChatGPT
   - Text Completion
2. Replicate through [Replicate](https://replicate.com)
   - Midjourney
   - Stable Diffusion
   - Other networks

Relicate offers many different networks. Initially I was only using image generation but recently discovered a [speech-to-text network](https://replicate.com/openai/whisper/api). Since you need to provide an audio to it, the easiest way I found is to use "reply" in your Telegram chat. Basically you select an audio message, reply to it with `/a` command (or whatever command you chose for the `openai/whisper` integration) and optionally provide language, for example `/a de`.

You may also need to change Bot Privacy settings:
https://stackoverflow.com/questions/50204633/allow-bot-to-access-telegram-group-messages

# Usage

## Authorization

You can whitelist/blacklist users and chats via the config file. Alternatively, set the admin_id and then use bot commands:

```sh
/whitelist user_id
/whitelist username
/whitelist chat_id
/blacklist user_id
/blacklist username
/blacklist chat_id
```

## Config

Create `config.toml`, fill `YOUR_TELEGRAM_TOKEN` and tokens for integrations:

```toml
debug = true

[general]
text_history_ttl = 300 # optional, for how long to store user messages, default 5 minutes
text_history_size = 10 # optional, how many messages from each user to keep

[telegram]
bot_token = "YOUR_TELEGRAM_TOKEN"
admin_id = 111 # optional, id of admin user who can whitelist and blacklist chats and users
allowed_users = [123, 234] # optional, a list of users from which messages are allowed
allowed_chats = [345, 456] # optional, a list of changes from which all messages are allowed

[integrations]

[integrations.openai]
api_key = "OPEN_AI_TOKEN" # set it to enable OpenAI integration
max_tokens = 1000 # max tokens to return by OpenAI text models, default 500
[[integrations.openai.networks]]
name = "completion"
version = "text-davinci-003"
command = "t" # Telegram command to trigger Text Completion requests
type = "text"
[[integrations.openai.networks]]
name = "chat"
version = "gpt-4"
command = "c" # Telegram command to trigger ChatGPT requests
type = "text"
[[integrations.openai.networks]]
name = "image"
version = "dalle"
command = "d" # Telegram command to trigger Dall-E requests
type = "text"

[integrations.replicate]
api_key = "REPLICATE_TOKEN" # set it to enable Replicate integration
[[integrations.replicate.networks]]
name = "tstramer/midjourney-diffusion"
version = "436b051ebd8f68d23e83d22de5e198e0995357afef113768c20f0b6fcef23c8b"
command = "m" # Telegram command to trigger Midjourney requests
type = "image"
[[integrations.replicate.networks]]
name = "stability-ai/stable-diffusion"
version = "f178fa7a1ae43a9a9af01b833b9d2ecf97b1bcb0acfd2b1c1c1c1c1c1c1c1c1c"
command = "s" # Telegram command to trigger Stable Diffusion requests
type = "image"
[[integrations.replicate.networks]]
name = "cjwbw/anything-v3.0"
version = "f410ed4c6a0c3bf8b76747860b3a3c9e4c8b5a827a16eac9dd5ad9642edce9a2"
command = "anything" # Telegram command to trigger requests to cjwbw/anything-v3.0
type = "image"
[[integrations.replicate.networks]]
name = "cjwbw/portraitplus"
version = "629a9fe82c7979c1dab323aedac2c03adaae2e1aecf6be278a51fde0245e20a4"
command = "portraitplus" # Telegram command to trigger requests to cjwbw/portraitplus
type = "image"
[[integrations.replicate.networks]]
name = "openai/whisper"
version = "e39e354773466b955265e969568deb7da217804d8e771ea8c9cd0cef6591f8bc" # Telegram command to trigger requests to openai/whisper speech-to-text model
command = "a"
type = "audio"
```

Explore Replicate [website](https://replicate.com/explore) to find more models.

## Running in development

```sh
# Start bot
make start
# Check logs
tail -f log.txt
```

## Running on the server

```sh
# Start bot
python -m src.bot &
# Stop bot
make stop
```

## Useful Telegram commands

```
# Test bot is alive
/ping
# Show available commands
/help
```

ChatGPT and Text Completion stores history of requests which can be manually cleaned using `clear` command.

```
/p clear
```

## Troubleshooting

- A request to the Telegram API was unsuccessful. Error code: 409. Description: Conflict: terminated by other getUpdates request; make sure that only one bot instance is running

You have another bot running on the background. Stop it with `make stop`, if it doesn't work find that process and kill it manually:

```sh
ps aux | grep "src.bot"
kill -9 <PID>
```
