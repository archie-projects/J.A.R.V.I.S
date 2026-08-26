import webrtcvad

from . import config


class UtteranceCapture:
    """Accumulates 20ms frames into one utterance, ending on a silence timeout."""

    def __init__(self):
        self.vad = webrtcvad.Vad(1)  # aggressiveness 0 (lenient) - 3 (strict); 1 is more forgiving of quieter mics
        self.reset()

    def reset(self):
        self.frames = []
        self.silence_ms = 0
        self.speech_started = False
        self.total_ms = 0

    def add_frame(self, frame_bytes: bytes) -> bool:
        """Returns True once the utterance is considered complete."""
        is_speech = self.vad.is_speech(frame_bytes, config.SAMPLE_RATE)
        self.frames.append(frame_bytes)
        self.total_ms += config.FRAME_MS

        if is_speech:
            self.speech_started = True
            self.silence_ms = 0
        elif self.speech_started:
            self.silence_ms += config.FRAME_MS

        if self.speech_started and self.silence_ms >= config.SILENCE_TIMEOUT_S * 1000:
            return True
        if self.total_ms >= config.MAX_UTTERANCE_S * 1000:
            return True
        return False

    def get_audio_bytes(self) -> bytes:
        return b"".join(self.frames)
