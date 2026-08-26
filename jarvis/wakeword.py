import numpy as np
from openwakeword.model import Model

from . import config

OWW_CHUNK_SAMPLES = 1280  # ~80ms at 16kHz, openWakeWord's expected chunk size


class WakeWordDetector:
    def __init__(self):
        # Point at the bundled hey_jarvis .onnx classifier by path — this version's
        # Model() takes wakeword_model_paths, not a bare model name.
        self.model = Model(wakeword_model_paths=[str(config.WAKE_WORD_MODEL_PATH)])
        self._buffer = np.zeros(0, dtype=np.int16)

    def feed(self, frame: np.ndarray) -> bool:
        """Feed one small frame (any length); returns True the moment the wake word fires."""
        self._buffer = np.concatenate([self._buffer, frame])
        triggered = False
        while len(self._buffer) >= OWW_CHUNK_SAMPLES:
            chunk, self._buffer = self._buffer[:OWW_CHUNK_SAMPLES], self._buffer[OWW_CHUNK_SAMPLES:]
            predictions = self.model.predict(chunk)
            score = predictions.get(config.WAKE_WORD_MODEL_NAME, 0.0)
            if score > config.WAKE_WORD_THRESHOLD:
                triggered = True
        return triggered
