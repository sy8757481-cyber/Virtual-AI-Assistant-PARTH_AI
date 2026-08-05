"""
==========================================
PARTH AI
Main Controller
==========================================
"""

from brain.agent import Agent

from voice.wake_word import WakeWord
from voice.speech_to_text import SpeechToText
from voice.text_to_speech import TextToSpeech

from utils.logger import log_info, log_error
import time


def main():

    try:

        wake = WakeWord()
        stt = SpeechToText()
        tts = TextToSpeech()

        agent = Agent()

        tts.speak("PARTH AI is now online.")

        while True:

            print("\n==============================")
            print("🎤 Waiting for Wake Word...")
            print("==============================")

            detected = wake.start_listening()

            if not detected:
                continue

            tts.speak("Yes?")

            time.sleep(1.5)

            command = stt.listen()

            if not command.strip():
                continue

            print(f"\nYou : {command}\n")

            if command.lower() in [
                "exit",
                "quit",
                "stop parth",
                "shutdown"
            ]:

                tts.speak("Shutting down.")
                break

            response = agent.execute(command)

            print("Agent Response :", response)

            if response:
                tts.speak(response)

        agent.close()

    except KeyboardInterrupt:

        print("\nStopping PARTH AI...")

    except Exception as e:

        log_error(f"Main Error : {e}")
        print(e)


if __name__ == "__main__":

    main()