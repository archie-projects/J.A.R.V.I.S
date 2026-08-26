import numpy as np
from faster_whisper import WhisperModel

_model = None


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        # Running on CPU for now — faster-whisper/CTranslate2 needs the full CUDA toolkit
        # (libcublas, libcudnn) for GPU inference, which we haven't installed. "small" model
        # with int8 quantization is genuinely fine on a modern CPU for short utterances, and
        # it leaves the full 8GB VRAM free for the LLM. Revisit CUDA for this in Phase 9 if
        # latency numbers say we need it.
        _model = WhisperModel("small", device="cpu", compute_type="int8")
    return _model


def transcribe_pcm(pcm_bytes: bytes) -> str:
    audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    model = get_model()
    segments, _ = model.transcribe(audio, language="en")
    text = " ".join(seg.text.strip() for seg in segments)
    return text.strip()
