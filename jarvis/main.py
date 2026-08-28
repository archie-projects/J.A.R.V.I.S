import queue
import time

from . import config
from . import audio
from .audio import make_input_stream
from .hotkey import PushToTalk
from .llm import Conversation
from .router import ModeRouter, ONLINE, OFFLINE
from .stt import transcribe_pcm
from .tts import speak
from .vad import UtteranceCapture
from .wakeword import WakeWordDetector

IDLE = "idle"
LISTENING = "listening"


def matches_any(text: str, phrases) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


def contains_deactivation(text: str) -> bool:
    return matches_any(text, config.DEACTIVATION_PHRASES)


def main():
    frame_queue: "queue.Queue" = queue.Queue()
    stream = make_input_stream(frame_queue)

    wake_detector = WakeWordDetector()
    ptt = PushToTalk()
    ptt.start()
    conversation = Conversation()
    router = ModeRouter(default_mode=OFFLINE)  # starts offline; say "go online" to switch

    state = IDLE
    utterance = None
    speech_start_wall_time = None

    print("JARVIS Phase 1+2 loop starting.")
    print(f"  Say 'Hey Jarvis' or press {config.PUSH_TO_TALK_KEY} to activate.")
    print(f"  Say one of {config.DEACTIVATION_PHRASES[:3]}... to deactivate.")
    print(f"  Say 'go online' / 'go offline' to switch modes. Currently: {router.preference}.")
    print("  Ctrl+C to quit.\n")

    stream.start()

    try:
        while True:
            frame = frame_queue.get()
            frame_bytes = frame.tobytes()

            if state == IDLE:
                woke = wake_detector.feed(frame)
                pushed = ptt.consume()
                if woke or pushed:
                    print("[jarvis] Wake triggered — listening...")
                    state = LISTENING
                    utterance = UtteranceCapture()
                    speech_start_wall_time = None
                    speak("Yes, sir?")
                continue

            # state == LISTENING
            was_speech_started = utterance.speech_started
            done = utterance.add_frame(frame_bytes)
            if utterance.speech_started and not was_speech_started:
                print("[jarvis] (hearing you...)")
                speech_start_wall_time = time.time()
            if not done:
                continue

            elapsed = time.time() - speech_start_wall_time if speech_start_wall_time else 0.0
            print(f"[jarvis] (processing... captured {utterance.total_ms}ms of audio, {elapsed:.2f}s wall time since speech started)")
            pcm = utterance.get_audio_bytes()
            utterance = UtteranceCapture()  # reset immediately for the next turn
            speech_start_wall_time = None

            # Mute the ENTIRE thinking window (STT + LLM + TTS), not just TTS playback.
            # Without this, the mic kept recording ambient noise/silence the whole time
            # we were transcribing/generating/speaking, building a backlog that got
            # misread as real speech the moment we resumed listening.
            audio.mute()
            try:
                text = transcribe_pcm(pcm)
                if not text:
                    print("[jarvis] (didn't catch that — still listening)")
                    continue

                print(f"[you] {text}")

                if contains_deactivation(text):
                    print("[jarvis] Standing down, sir.")
                    speak("Standing down, sir.")
                    state = IDLE
                    wake_detector = WakeWordDetector()  # clean buffer, cheaply
                    continue

                if matches_any(text, config.MODE_SWITCH_ONLINE_PHRASES):
                    router.set_online()
                    print("[jarvis] Switching to online mode, sir.")
                    speak("Switching to online mode, sir.")
                    continue

                if matches_any(text, config.MODE_SWITCH_OFFLINE_PHRASES):
                    router.set_offline()
                    print("[jarvis] Switching to offline mode, sir.")
                    speak("Switching to offline mode, sir.")
                    continue

                backend, notice = router.resolve_backend()
                if notice:
                    print(f"[jarvis] {notice}")
                    speak(notice)

                reply = conversation.ask(text, backend=backend)
                print(f"[jarvis] ({backend}) {reply}")
                speak(reply)
                # stays in LISTENING for the next turn — no wake word needed until deactivation
            finally:
                audio.unmute()
                audio.drain_queue(frame_queue)

    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        stream.stop()
        stream.close()


if __name__ == "__main__":
    main()
