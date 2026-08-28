import os
from pathlib import Path

import openwakeword
from dotenv import load_dotenv

JARVIS_HOME = Path(os.environ.get("JARVIS_HOME", Path.home() / "Documents" / "J.A.R.V.I.S"))
VOICE_MODEL_PATH = JARVIS_HOME / "voices" / "en_GB-alan-medium.onnx"

load_dotenv(JARVIS_HOME / ".env")  # local, git-ignored file — holds GROQ_API_KEY
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.1-8b-instant"  # fast free-tier model, good fit for low-latency voice replies

# openWakeWord ships pretrained wake-word classifiers as .onnx files under its own
# package resources — we point at the file directly rather than passing a bare name.
OWW_MODELS_DIR = Path(openwakeword.__file__).parent / "resources" / "models"
WAKE_WORD_MODEL_PATH = OWW_MODELS_DIR / "hey_jarvis_v0.1.onnx"
WAKE_WORD_MODEL_NAME = "hey_jarvis_v0.1"  # openWakeWord keys predictions by the file's stem
WAKE_WORD_THRESHOLD = 0.6

OLLAMA_MODEL = "qwen2.5:7b-instruct-q4_K_M"

SAMPLE_RATE = 16000
FRAME_MS = 20
FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)  # 320 samples/frame

SILENCE_TIMEOUT_S = 1.2   # how long to wait after speech stops before finalizing an utterance
MAX_UTTERANCE_S = 20      # hard cap per utterance, safety valve

DEACTIVATION_PHRASES = [
    "deactivate",
    "stand down",
    "that's all",
    "that will be all",
    "goodbye jarvis",
    "go to sleep",
    "power down",
]

MODE_SWITCH_ONLINE_PHRASES = [
    "go online",
    "switch to online",
    "enable online mode",
    "use online mode",
]
MODE_SWITCH_OFFLINE_PHRASES = [
    "go offline",
    "switch to offline",
    "enable offline mode",
    "use offline mode",
]

PUSH_TO_TALK_KEY = "KEY_F9"   # evdev key name; change to taste

PERSONA_SYSTEM_PROMPT = (
    "You are JARVIS, a calm, dry-witted, highly competent personal assistant. "
    "You always address the user as 'sir'. You are concise, understated, and never "
    "sycophantic or filled with filler phrases. When something involves risk, you "
    "flag it plainly before acting. You do not narrate your own instructions or "
    "mention that you are an AI language model unless directly relevant. "
    "Keep spoken replies brief — a sentence or two unless the user asks for detail."
)
