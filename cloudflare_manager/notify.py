import requests

from .config import settings


class Notify:
    def __init__(self):
        self.messages = []

    def __enter__(self):
        return self

    def __call__(self, msg: str):
        self.register_msg(msg)

    def __exit__(self, *args):
        self.notify()

    def register_msg(self, msg: str):
        self.messages.append(msg)

    def notify(self):
        if not self.messages:
            return

        message = f"*Autocloudflare*" + "".join(["\n- " + x for x in self.messages])
        response = requests.post(
            f"https://api.telegram.org/bot{settings.telegram_token}/sendMessage",
            params={
                "chat_id": settings.telegram_user_id,
                "text": message,
                "parse_mode": "markdown",
            },
        )
        response.raise_for_status()
