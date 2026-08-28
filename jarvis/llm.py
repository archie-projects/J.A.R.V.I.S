import ollama
from groq import Groq

from . import config


class Conversation:
    """Holds message history for one 'active session' (wake word to deactivation).
    Same history is used regardless of which backend (online/offline) answers a
    given turn, so switching modes mid-conversation doesn't lose context."""

    def __init__(self):
        self.messages = [{"role": "system", "content": config.PERSONA_SYSTEM_PROMPT}]
        self._groq_client = Groq(api_key=config.GROQ_API_KEY) if config.GROQ_API_KEY else None

    def ask(self, user_text: str, backend: str = "offline") -> str:
        self.messages.append({"role": "user", "content": user_text})

        if backend == "online" and self._groq_client:
            response = self._groq_client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=self.messages,
            )
            reply = response.choices[0].message.content
        else:
            response = ollama.chat(model=config.OLLAMA_MODEL, messages=self.messages)
            reply = response["message"]["content"]

        self.messages.append({"role": "assistant", "content": reply})
        return reply
