# Language Tutor Telegram Bot

A conversational language tutor you can run from your own server. It pitches its language just above your current level, keeps replies short and chat-like, and corrects mistakes inline.

## Setup

1. Create a bot via [@BotFather](https://t.me/BotFather) on Telegram (`/newbot`) and copy the token
2. Get an Anthropic API key from [console.anthropic.com](https://console.anthropic.com)
3. Copy `.env.example` to `.env` and fill in both keys:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```
4. Whitelist yourself by adding your Telegram user ID to `whitelist.json` (see `whitelist.json.template`). You can find your ID by messaging [@userinfobot](https://t.me/userinfobot).
5. Install dependencies and run:
   ```
   uv run python main.py
   ```

## Usage

| Command  | Description                              |
|----------|------------------------------------------|
| `/start` | Start or restart the conversation        |
| `/reset` | Clear conversation history and start fresh |
| `/preference` | View your current preferences |
| `/preference <text>` | Add or update preferences (e.g. `/preference I'm a beginner and prefer formal speech`) |

Just send messages in the target language (or English to start). The bot will:
- Reply at a level just above yours
- Introduce slightly more advanced vocabulary and grammar naturally over time
- Append a correction block when you make errors

The last 10 exchanges are kept as context for the conversation.
