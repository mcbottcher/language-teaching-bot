import os
import functools
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WHITELIST_FILE = os.path.join(os.path.dirname(__file__), "whitelist.txt")


def load_whitelist() -> set[int]:
    if not os.path.exists(WHITELIST_FILE):
        return set()
    with open(WHITELIST_FILE) as f:
        ids = set()
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                ids.add(int(line))
        return ids


def whitelist_only(func):
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id not in load_whitelist():
            await update.message.reply_text("Sorry, you don't have access to this bot.")
            return
        return await func(update, context)
    return wrapper


@whitelist_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello! I'm your language teaching bot. Send me a message!")


@whitelist_only
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    text = update.message.text
    print(f"[{user.username or user.first_name}] {text}")
    await update.message.reply_text(f"You said: {text}")


def main() -> None:
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
