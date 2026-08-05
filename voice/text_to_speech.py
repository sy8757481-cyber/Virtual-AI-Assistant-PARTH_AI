"""
==========================================
PARTH AI
Text To Speech Module
==========================================
"""

import pyttsx3
from config import VOICE_RATE, VOICE_VOLUME
from utils.logger import log_info, log_error



class TextToSpeech:

    def __init__(self):

        try:

            self.engine = pyttsx3.init()

            self.engine.setProperty("rate", VOICE_RATE)
            self.engine.setProperty("volume", VOICE_VOLUME)

            self.voices = self.engine.getProperty("voices")

            if self.voices:
                self.engine.setProperty("voice", self.voices[0].id)

            log_info("Text To Speech Initialized Successfully.")

        except Exception as e:

            log_error(f"TTS Initialization Error : {e}")

    # --------------------------------------
    # Speak
    # --------------------------------------

    def speak(self, text: str):

        try:

            if not text:
                return

            text = str(text).strip()

            if text == "":
                return

            log_info(f"Assistant Said : {text}")

            self.engine.stop()

            self.engine.say(text)

            self.engine.runAndWait()

        except Exception as e:

            log_error(f"TTS Speak Error : {e}")

    # --------------------------------------
    # Stop Speaking
    # --------------------------------------

    def stop(self):

        try:

            self.engine.stop()

            log_info("Speech Stopped")

        except Exception as e:

            log_error(f"TTS Stop Error : {e}")

    # --------------------------------------
    # Change Voice
    # --------------------------------------

    def set_voice(self, index=0):

        try:

            if 0 <= index < len(self.voices):

                self.engine.setProperty(
                    "voice",
                    self.voices[index].id
                )

                log_info(f"Voice Changed : {index}")

        except Exception as e:

            log_error(f"Voice Change Error : {e}")