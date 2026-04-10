import os
from pathlib import Path
from dotenv import load_dotenv

import db
import llm
from bot_core import BotCore
from telegram_interface import TelegramInterface

load_dotenv()

PROMPTS_DIR = Path(__file__).parent / "prompts"
WHITELIST_FILE = Path(__file__).parent / "whitelist.json"


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")
    if not llm.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY not set in .env")

    db.init_db()

    core = BotCore(
        whitelist_file=WHITELIST_FILE,
        base_system_prompt=(PROMPTS_DIR / "system.txt").read_text(),
        preference_prompt=(PROMPTS_DIR / "preference_update.txt").read_text(),
    )
    TelegramInterface(token=token, core=core).run()


if __name__ == "__main__":
    main()
