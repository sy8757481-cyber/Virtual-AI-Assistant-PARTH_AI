"""
==========================================
PARTH AI
Main Controller — incremental correction
==========================================
"""

import re
import time

from brain.agent import Agent
from voice.wake_word import WakeWord
from voice.speech_to_text import SpeechToText
from voice.text_to_speech import TextToSpeech
from utils.logger import log_error


SLEEP_COMMANDS = {
    "sleep", "go to sleep", "stop listening", "stop listening parth"
}

SHUTDOWN_COMMANDS = {
    "exit", "quit", "stop parth", "shutdown", "goodbye", "good bye"
}


def normalize_control_command(command: str) -> str:
    """Normalize only for sleep/exit matching; preserve the original task."""
    text = re.sub(r"[^\w\s]", " ", command.casefold())
    return " ".join(text.split())


def get_acknowledgement(command: str) -> str:
    """Retained for compatibility. The Agent supplies one final response."""
    return ""


def speak_text(text: str, tts=None):
    """Use the corrected TTS module's blocking speech subprocess."""
    if text is None or not str(text).strip():
        return False
    try:
        if tts is None:
            tts = TextToSpeech()
        success = tts.speak(str(text).strip())
        if not success:
            print("TTS could not complete. Check the PARTH log.")
        return success
    except Exception as e:
        log_error(f"TTS Error : {e}")
        print(f"TTS Error : {e}")
        return False


def main():
    wake = None
    stt = None
    tts = None
    agent = None

    try:
        wake = WakeWord()
        stt = SpeechToText()
        tts = TextToSpeech()
        agent = Agent()

        speak_text("PARTH AI is now online.", tts)
        print("\n==============================")
        print("      PARTH AI ONLINE")
        print("==============================")

        # Wake-word mode
        while True:
            print("\n==============================")
            print("🎤 Waiting for Wake Word...")
            print("==============================")

            detected = wake.start_listening()
            if not detected:
                continue

            print("\n🔊 PARTH : Yes sir?")
            time.sleep(1.0)
            if speak_text("Yes sir?", tts):
                print("✅ Wake response finished.")
            time.sleep(1.5)

            # Continuous command mode
            while True:
                command = stt.listen()
                if not isinstance(command, str) or not command.strip():
                    continue
                command = command.strip()
                print(f"\nYou : {command}")
                command_lower = normalize_control_command(command)

                if command_lower in SLEEP_COMMANDS:
                    speak_text("Okay sir. Going to sleep.", tts)
                    print("😴 PARTH : Sleeping. Say Hey Jarvis to wake me.")
                    break

                # Exact command matching prevents a song/search containing
                # the words 'good' and 'bye' from shutting down PARTH.
                if command_lower in SHUTDOWN_COMMANDS:
                    print("🔴 PARTH : Shutting down.")
                    speak_text("Shutting down, sir.", tts)
                    time.sleep(1)
                    return

                # One execution, one spoken result. Keep the original text
                # so URLs, decimal numbers and arithmetic are not altered.
                result = agent.execute(command)
                if result:
                    speak_text(result, tts)

            # Sleep returns to wake-word mode, never directly to STT.
            print("\n😴 PARTH is sleeping...")
            print("🎤 Say Hey Jarvis to wake me.")
            time.sleep(2.0)

    except KeyboardInterrupt:
        print("\nPARTH AI stopped.")
    except Exception as e:
        log_error(f"Main Error : {e}")
        print(f"\n❌ Main Error : {e}")
    finally:
        # A failed cleanup must not prevent the remaining cleanup attempts.
        for component, method in (
            (wake, "stop"), (tts, "stop"), (agent, "close")
        ):
            if component is not None:
                try:
                    getattr(component, method)()
                except Exception as e:
                    log_error(f"Cleanup Error ({method}) : {e}")


if __name__ == "__main__":
    main()
