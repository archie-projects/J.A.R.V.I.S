import threading

import evdev
from evdev import ecodes

from . import config


def find_keyboard_devices():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    keyboards = [
        d for d in devices
        if ecodes.EV_KEY in d.capabilities() and ecodes.KEY_A in d.capabilities().get(ecodes.EV_KEY, [])
    ]
    return keyboards


class PushToTalk:
    """Reads raw keyboard events via evdev (requires the 'input' group — set up in Phase 0).
    This works under Wayland/Hyprland where X11-style global hotkey libraries (pynput) don't."""

    def __init__(self):
        self.triggered = threading.Event()
        self._keycode = getattr(ecodes, config.PUSH_TO_TALK_KEY)
        self._devices = find_keyboard_devices()
        if not self._devices:
            print(
                "[hotkey] WARNING: no keyboard input devices found — push-to-talk disabled "
                "for this run. Wake word still works. Check 'groups' includes 'input' "
                "(needs a logout/login after Phase 0 if you haven't done that yet)."
            )

    def start(self) -> None:
        for dev in self._devices:
            threading.Thread(target=self._listen, args=(dev,), daemon=True).start()

    def _listen(self, dev) -> None:
        try:
            for event in dev.read_loop():
                if event.type == ecodes.EV_KEY and event.code == self._keycode and event.value == 1:
                    self.triggered.set()
        except Exception as e:
            print(f"[hotkey] listener error on {dev.path}: {e}")

    def consume(self) -> bool:
        if self.triggered.is_set():
            self.triggered.clear()
            return True
        return False
