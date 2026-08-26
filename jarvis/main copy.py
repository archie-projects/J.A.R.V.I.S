import queue

from . import config
from .audio import make_input_stream
from .hotkey import PushToTalk
from .llm import Conversation
from .stt import transcribe_pcm
from .tts import speak
from .vad import UtteranceCapture
from .wakeword import WakeWordDetector

IDLE = "idle"
LISTENING = "listening"


def contains_deactivation(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in config.DEACTIVATION_PHRASES)


def main():
    frame_queue: "queue.Queue" = queue.Queue()
    stream = make_input_stream(frame_queue)

    wake_detector = WakeWordDetector()
    ptt = PushToTalk()
    ptt.start()
    conversation = Conversation()

    state = IDLE
    utterance = None

    print("JARVIS Phase 1 loop starting.")
    print(f"  Say 'Hey Jarvis' or press {config.PUSH_TO_TALK_KEY} to activate.")
    print(f"  Say one of {config.DEACTIVATION_PHRASES[:3]}... to deactivate.")
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
                    speak("Yes, sir?")
                continue

            # state == LISTENING
            done = utterance.add_frame(frame_bytes)
            if not done:
                continue

            pcm = utterance.get_audio_bytes()
            utterance = UtteranceCapture()  # reset immediately for the next turn

            text = transcribe_pcm(pcm)
            if not text:
                # nothing intelligible heard — stay in LISTENING, don't require the wake word again
                continue

            print(f"[you] {text}")

            if contains_deactivation(text):
                speak("Standing down, sir.")
                state = IDLE
                continue

            reply = conversation.ask(text)
            print(f"[jarvis] {reply}")
            speak(reply)
            # stays in LISTENING for the next turn — no wake word needed until deactivation

    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        stream.stop()
        stream.close()


if __name__ == "__main__":
    main()
