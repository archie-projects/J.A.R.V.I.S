import queue
import threading
import time

import numpy as np
import sounddevice as sd

from . import config

# Set while JARVIS is speaking, so the mic doesn't pick up and react to its own voice
# (important on speaker setups without echo cancellation — this was causing false
# wake-word/deactivation triggers).
MIC_MUTED = threading.Event()


def make_input_stream(frame_queue: "queue.Queue[np.ndarray]") -> sd.InputStream:
    """Continuous mic capture, pushing int16 frames of FRAME_SAMPLES length onto frame_queue.
    Uses whatever PipeWire presents as the default input device."""

    def callback(indata, frames, time_info, status):
        if status:
            print(f"[audio] status: {status}")
        if MIC_MUTED.is_set():
            return  # drop frames entirely while JARVIS is talking
        frame_queue.put(indata.copy().reshape(-1))

    stream = sd.InputStream(
        samplerate=config.SAMPLE_RATE,
        channels=1,
        dtype="int16",
        blocksize=config.FRAME_SAMPLES,
        callback=callback,
    )
    return stream


def play_audio(pcm_int16: np.ndarray, sample_rate: int) -> None:
    MIC_MUTED.set()
    try:
        sd.play(pcm_int16, sample_rate)
        sd.wait()
        time.sleep(0.15)  # small buffer only; headphones mean no real speaker echo to wait out
    finally:
        MIC_MUTED.clear()


def mute() -> None:
    MIC_MUTED.set()


def unmute() -> None:
    MIC_MUTED.clear()


def drain_queue(q: "queue.Queue") -> None:
    """Discard any backlogged frames (e.g. ones queued right at a mute/unmute boundary)."""
    while True:
        try:
            q.get_nowait()
        except queue.Empty:
            break
