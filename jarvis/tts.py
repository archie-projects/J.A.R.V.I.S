import numpy as np
from piper import PiperVoice

from . import config
from .audio import play_audio

_voice = None


def get_voice() -> PiperVoice:
    global _voice
    if _voice is None:
        _voice = PiperVoice.load(str(config.VOICE_MODEL_PATH))
    return _voice


def speak(text: str) -> None:
    """Synthesize and play text aloud.
    NOTE: this is our first integration pass against the piper-tts Python API —
    if this throws an AttributeError, tell me the exact error and we'll adjust
    to match the installed piper-tts version's real interface."""
    voice = get_voice()
    chunks = []
    for audio_chunk in voice.synthesize(text):
        chunks.append(np.frombuffer(audio_chunk.audio_int16_bytes, dtype=np.int16))
    if chunks:
        pcm = np.concatenate(chunks)
        play_audio(pcm, voice.config.sample_rate)
