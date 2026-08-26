import ollama

from . import config


class Conversation:
    """Holds message history for one 'active session' (wake word to deactivation)."""

    def __init__(self):
        self.messages = [{"role": "system", "content": config.PERSONA_SYSTEM_PROMPT}]

    def ask(self, user_text: str) -> str:
        self.messages.append({"role": "user", "content": user_text})
        response = ollama.chat(model=config.OLLAMA_MODEL, messages=self.messages)
        reply = response["message"]["content"]
        self.messages.append({"role": "assistant", "content": reply})
        return reply
