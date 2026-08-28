from . import config
from .connectivity import is_online

ONLINE = "online"
OFFLINE = "offline"


class ModeRouter:
    """Tracks the user's preferred mode (online/offline) and resolves it against
    real availability (API key present, internet reachable) each turn, falling
    back to offline transparently — with a spoken notice only the first time."""

    def __init__(self, default_mode: str = OFFLINE):
        self.preference = default_mode
        self._fallback_notified = False

    def set_online(self) -> None:
        self.preference = ONLINE
        self._fallback_notified = False

    def set_offline(self) -> None:
        self.preference = OFFLINE
        self._fallback_notified = False

    def resolve_backend(self) -> tuple[str, str | None]:
        """Returns (backend_to_use, spoken_notice_or_None)."""
        if self.preference == OFFLINE:
            return OFFLINE, None

        if not config.GROQ_API_KEY:
            notice = None
            if not self._fallback_notified:
                notice = "No Groq API key configured yet, sir — staying in offline mode."
                self._fallback_notified = True
            return OFFLINE, notice

        if not is_online():
            notice = None
            if not self._fallback_notified:
                notice = "No internet connection, sir — falling back to offline mode."
                self._fallback_notified = True
            return OFFLINE, notice

        self._fallback_notified = False
        return ONLINE, None
