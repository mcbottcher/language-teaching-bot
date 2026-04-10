from abc import ABC, abstractmethod


class MessagingInterface(ABC):
    @abstractmethod
    async def send_message(self, user_id: str, text: str) -> None:
        """Send a text message to the given user."""
        ...
