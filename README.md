# Installation

Python 3.10+ is required.

```sh
# Create Virtual environment
python3.10 -m venv venv
# Activate it
source venv/bin/activate
# Install dependencies
pip install -r requirements.txt
```

# Available integrations

1. Dall-E through [Official API](https://beta.openai.com/docs/introduction)
2. ChatGPT through [Official API](https://beta.openai.com/docs/introduction)
3. Midjourney through [Replicate](https://replicate.com/tstramer/midjourney-diffusion)
4. Stable Diffusion through [Replicate](https://replicate.com/tstramer/midjourney-diffusion)

# Usage

## Config

Sample `config.toml`:

```toml
DEBUG = true

[general]
TEXT_HISTORY_TTL = 300 # for how long to store user messages, default 5 minutes
TEXT_HISTORY_SIZE = 10 # how many messages from each user to keep
IMAGE_HISTORY_TTL = 300 # for how long to store the last image from user, default 5 minutes

[telegram]
BOT_TOKEN = "YOUR_TELEGRAM_TOKEN"
ALLOWED_USERS = [123, 234] # optional, a list of users from which messages are allowed
ALLOWED_CHATS = [345, 456] # optional, a list of changes from which all messages are allowed

[integrations]
[integrations.openai]
API_KEY = "OPEN_AI_TOKEN" # set it to enable OpenAI integration
DALLE_COMMAND = "a" # optional, command to trigger Dall-E requests, default "d"
CHATGPT_COMMAND = "b" # optional, command to trigger ChatGPT requests, default "p"
[integrations.replicate]
API_KEY = "REPLICATE_TOKEN" # set it to enable Midjourney integration
MIDJOURNEY_COMMAND = "c" # optional, command to trigger Midjourney requests, default "m"
STABLE_DIFFUSION_COMMAND = "d" # optional, command to trigger Stable Diffusion requests, default "s"
```

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
```

Integrations that store requests and responses in history also support a `clear` command to clean the state.

```
# Clear previous image from OpenAI Dall-E integration
/d clear
# Clear history of previous messages from OpenAI ChatGPT integration
/p clear
```

OpenAI Dall-E supports image editing, to edit previous image type `adjust`:

```
/d adjust Sun should be blue and stars should be green
```