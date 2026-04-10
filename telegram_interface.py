from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from bot_core import BotCore


class TelegramInterface:
    def __init__(self, token: str, core: BotCore):
        self.core = core
        self.app = ApplicationBuilder().token(token).build()
        self.app.add_handler(CommandHandler("start", self._start))
        self.app.add_handler(CommandHandler("reset", self._reset))
        self.app.add_handler(CommandHandler("preference", self._preference))
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
        )

    def _user_id(self, update: Update) -> str:
        return str(update.effective_user.id)

    def _display_name(self, update: Update) -> str:
        u = update.effective_user
        return u.username or u.first_name

    async def _guard(self, update: Update) -> bool:
        if not self.core.is_allowed(self._user_id(update)):
            await update.message.reply_text("Sorry, you don't have access to this bot.")
            return False
        return True

    async def _start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self._guard(update):
            return
        reply = self.core.handle_start(self._user_id(update), self._display_name(update))
        await update.message.reply_text(reply)

    async def _reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self._guard(update):
            return
        reply = self.core.handle_reset(self._user_id(update))
        await update.message.reply_text(reply)

    async def _preference(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self._guard(update):
            return
        new_pref = " ".join(context.args or []).strip()
        if not new_pref:
            reply = self.core.handle_preference_read(self._user_id(update))
        else:
            reply = self.core.handle_preference_set(
                self._user_id(update), self._display_name(update), new_pref
            )
        await update.message.reply_text(reply)

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self._guard(update):
            return
        reply = self.core.handle_message(
            self._user_id(update), self._display_name(update), update.message.text
        )
        await update.message.reply_text(reply)

    def run(self) -> None:
        print("Bot is running. Press Ctrl+C to stop.")
        self.app.run_polling()
