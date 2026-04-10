import json
from collections import deque
from pathlib import Path

import db
import llm


class BotCore:
    def __init__(
        self,
        whitelist_file: Path,
        base_system_prompt: str,
        preference_prompt: str,
    ):
        self.whitelist_file = whitelist_file
        self.base_system_prompt = base_system_prompt
        self.preference_prompt = preference_prompt
        self._histories: dict[str, deque] = {}

    def load_whitelist(self) -> dict[str, dict]:
        if not self.whitelist_file.exists():
            return {}
        data = json.loads(self.whitelist_file.read_text())
        return {str(k): v for k, v in data.items()}

    def is_allowed(self, user_id: str) -> bool:
        return user_id in self.load_whitelist()

    def get_user_language(self, user_id: str) -> str:
        entry = self.load_whitelist().get(user_id, {})
        return entry.get("language", "the target language")

    def get_history(self, user_id: str) -> deque:
        if user_id not in self._histories:
            self._histories[user_id] = deque(maxlen=20)
        return self._histories[user_id]

    def build_system_prompt(self, user_id: str) -> str:
        language = self.get_user_language(user_id)
        prompt = self.base_system_prompt + f"\nThe user is learning: {language}"
        prefs = db.get_preferences(user_id)
        if prefs:
            prompt += f"\nUser preferences:\n{prefs}"
        return prompt

    def handle_start(self, user_id: str, display_name: str) -> str:
        db.ensure_user(user_id, display_name)
        self.get_history(user_id).clear()
        language = self.get_user_language(user_id)
        return (
            f"Hello! I'm your {language} tutor. What would you like to talk about today?\n\n"
            "Use /reset to start a fresh conversation, or /preference to update your preferences."
        )

    def handle_reset(self, user_id: str) -> str:
        self.get_history(user_id).clear()
        return "Conversation reset. What would you like to talk about?"

    def handle_preference_read(self, user_id: str) -> str:
        prefs = db.get_preferences(user_id)
        if prefs:
            return f"Your current preferences:\n\n{prefs}"
        return (
            "You have no preferences set yet. Use /preference <text> to add some.\n"
            "Example: /preference My name is Ana and I'm a beginner"
        )

    def handle_preference_set(self, user_id: str, display_name: str, new_pref: str) -> str:
        db.ensure_user(user_id, display_name)
        existing = db.get_preferences(user_id)
        chat_result = llm.chat(
            [{"role": "user", "content": self.preference_prompt.format(
                existing=existing or "(none)", new=new_pref
            )}],
            max_tokens=512,
        )
        updated = chat_result.text.strip()
        db.add_tokens(user_id, chat_result.input_tokens, chat_result.output_tokens)
        db.set_preferences(user_id, updated)
        return f"Preferences updated:\n\n{updated}"

    def handle_message(self, user_id: str, display_name: str, text: str) -> str:
        print(f"[{display_name}] {text}")
        db.ensure_user(user_id, display_name)
        history = self.get_history(user_id)
        history.append({"role": "user", "content": text})
        chat_result = llm.chat(
            list(history),
            system=self.build_system_prompt(user_id),
        )
        db.add_tokens(user_id, chat_result.input_tokens, chat_result.output_tokens)
        history.append({"role": "assistant", "content": chat_result.text})
        print(f"[bot -> {display_name}] {chat_result.text}")
        return chat_result.text
