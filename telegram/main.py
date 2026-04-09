import os
import functools
from collections import deque
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import anthropic

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
WHITELIST_FILE = os.path.join(os.path.dirname(__file__), "whitelist.txt")

SYSTEM_PROMPT = """You are a Spanish language tutor in a friendly, conversational chat.

Your core behavior:
- Respond primarily in Spanish, but pitch your vocabulary and grammar just slightly above what the student demonstrates. If they use simple present tense with basic vocab, reply using mostly simple constructions but introduce one or two slightly more advanced phrases naturally.
- Keep replies conversational and short (2–4 sentences), as if chatting over text.
- At the end of each reply, if the student made any Spanish mistakes (grammar, spelling, word choice, accents), add a brief correction section separated by a line like this:

---
Correction: [quote the mistake] → [corrected form] — [one-line explanation in English]

Only correct genuine errors, not stylistic choices. If there are no mistakes, omit the correction section entirely.
- If the student writes in English, gently encourage them to try in Spanish, but still respond helpfully."""

# Last 10 user messages + their assistant replies (20 entries max)
conversation_history: deque = deque(maxlen=20)


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
    conversation_history.clear()
    await update.message.reply_text(
        "Hola! Soy tu tutor de español. ¿De qué quieres hablar hoy?\n\n"
        "(Hello! I'm your Spanish tutor. What would you like to talk about today?)\n\n"
        "Use /reset at any time to start a fresh conversation."
    )


@whitelist_only
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    conversation_history.clear()
    await update.message.reply_text("Conversation reset. Empecemos de nuevo — ¿de qué quieres hablar?")


@whitelist_only
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    text = update.message.text
    print(f"[{user.username or user.first_name}] {text}")

    conversation_history.append({"role": "user", "content": text})

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=list(conversation_history),
    )

    reply = response.content[0].text
    conversation_history.append({"role": "assistant", "content": reply})

    print(f"[bot -> {user.username or user.first_name}] {reply}")
    await update.message.reply_text(reply)


def main() -> None:
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set in .env")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
