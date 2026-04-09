# Spanish Tutor Telegram Bot

A conversational Spanish tutor powered by Claude. It pitches its language just above your current level, keeps replies short and chat-like, and corrects mistakes inline.

## Setup

1. Create a bot via [@BotFather](https://t.me/BotFather) on Telegram (`/newbot`) and copy the token
2. Get an Anthropic API key from [console.anthropic.com](https://console.anthropic.com)
3. Copy `.env.example` to `.env` and fill in both keys:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```
4. Whitelist yourself by adding your Telegram user ID to `whitelist.txt` (one ID per line). You can find your ID by messaging [@userinfobot](https://t.me/userinfobot).
5. Install dependencies and run:
   ```
   uv run python main.py
   ```

## Usage

| Command  | Description                              |
|----------|------------------------------------------|
| `/start` | Start or restart the conversation        |
| `/reset` | Clear conversation history and start fresh |

Just send messages in Spanish (or English to start). The bot will:
- Reply in Spanish at a level just above yours
- Introduce slightly more advanced vocabulary and grammar naturally over time
- Append a correction block when you make errors, e.g.:

  ```
  ---
  Correction: "yo soy cansado" → "yo estoy cansado" — use estar for temporary states
  ```

The last 10 exchanges are kept as context for the conversation.
