import queue

import numpy as np
import sounddevice as sd

from . import config


def make_input_stream(frame_queue: "queue.Queue[np.ndarray]") -> sd.InputStream:
    """Continuous mic capture, pushing int16 frames of FRAME_SAMPLES length onto frame_queue.
    Uses whatever PipeWire presents as the default input device."""

    def callback(indata, frames, time_info, status):
        if status:
            print(f"[audio] status: {status}")
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
    sd.play(pcm_int16, sample_rate)
    sd.wait()
