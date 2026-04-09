import functools
import json
from collections import deque
from pathlib import Path
from dotenv import load_dotenv
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

import db
import llm

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WHITELIST_FILE = Path(__file__).parent / "whitelist.json"
PROMPTS_DIR = Path(__file__).parent / "prompts"

BASE_SYSTEM_PROMPT = (PROMPTS_DIR / "system.txt").read_text()
PREFERENCE_PROMPT = (PROMPTS_DIR / "preference_update.txt").read_text()

# Per-user conversation history: telegram_id -> deque of message dicts
conversation_histories: dict[int, deque] = {}


def get_history(user_id: int) -> deque:
    if user_id not in conversation_histories:
        conversation_histories[user_id] = deque(maxlen=20)
    return conversation_histories[user_id]


def load_whitelist() -> dict[int, dict]:
    if not WHITELIST_FILE.exists():
        return {}
    data = json.loads(WHITELIST_FILE.read_text())
    return {int(k): v for k, v in data.items()}


def get_user_language(user_id: int) -> str:
    entry = load_whitelist().get(user_id, {})
    return entry.get("language", "the target language")


def build_system_prompt(user_id: int) -> str:
    language = get_user_language(user_id)
    prompt = BASE_SYSTEM_PROMPT + f"\nThe user is learning: {language}"
    prefs = db.get_preferences(user_id)
    if prefs:
        prompt += f"\nUser preferences:\n{prefs}"
    return prompt


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
    user = update.effective_user
    db.ensure_user(user.id, user.first_name)
    get_history(user.id).clear()
    language = get_user_language(user.id)
    await update.message.reply_text(
        f"Hello! I'm your {language} tutor. What would you like to talk about today?\n\n"
        "Use /reset to start a fresh conversation, or /preference to update your preferences."
    )


@whitelist_only
async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    get_history(update.effective_user.id).clear()
    await update.message.reply_text("Conversation reset. What would you like to talk about?")


@whitelist_only
async def preference(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    new_pref = " ".join(context.args).strip()
    if not new_pref:
        prefs = db.get_preferences(user.id)
        if prefs:
            await update.message.reply_text(f"Your current preferences:\n\n{prefs}")
        else:
            await update.message.reply_text(
                "You have no preferences set yet. Use /preference <text> to add some.\n"
                "Example: /preference My name is Ana and I'm a beginner"
            )
        return

    db.ensure_user(user.id, user.first_name)
    existing = db.get_preferences(user.id)

    chat_result = llm.chat(
        [{"role": "user", "content": PREFERENCE_PROMPT.format(existing=existing or "(none)", new=new_pref)}],
        max_tokens=512,
    )
    updated = chat_result.text.strip()
    db.add_tokens(user.id, chat_result.input_tokens, chat_result.output_tokens)
    db.set_preferences(user.id, updated)
    await update.message.reply_text(f"Preferences updated:\n\n{updated}")


@whitelist_only
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    text = update.message.text
    print(f"[{user.username or user.first_name}] {text}")

    db.ensure_user(user.id, user.first_name)
    history = get_history(user.id)
    history.append({"role": "user", "content": text})

    chat_result = llm.chat(
        list(history),
        system=build_system_prompt(user.id),
    )
    db.add_tokens(user.id, chat_result.input_tokens, chat_result.output_tokens)
    history.append({"role": "assistant", "content": chat_result.text})

    print(f"[bot -> {user.username or user.first_name}] {chat_result.text}")
    await update.message.reply_text(chat_result.text)


def main() -> None:
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")
    if not llm.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set in .env")

    db.init_db()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("preference", preference))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running. Press Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
