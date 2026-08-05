"""
==========================================
PARTH AI
Speech To Text Module
==========================================
"""

import os
import tempfile

import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel

from utils.logger import log_info, log_error


class SpeechToText:

    def __init__(self):

        try:

            self.sample_rate = 16000

            self.model = WhisperModel(
                "tiny",
                device="cpu",
                compute_type="int8"
            )

            log_info("Speech To Text Initialized Successfully.")

        except Exception as e:

            log_error(f"STT Initialization Error : {e}")

    def listen(self, duration=5):

        temp_file = None

        try:

            print("\n🎤 Listening...")

            audio = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                dtype="int16"
            )

            sd.wait()

            with tempfile.NamedTemporaryFile(
                suffix=".wav",
                delete=False
            ) as file:

                temp_file = file.name

                write(
                    temp_file,
                    self.sample_rate,
                    audio
                )

            segments, _ = self.model.transcribe(
                temp_file,
                language=None
            )

            text = ""

            for segment in segments:
                text += segment.text

            text = text.strip()

            print(f"🗣 You Said : {text}")

            log_info(f"User Said : {text}")

            return text

        except Exception as e:

            log_error(f"Speech Error : {e}")

            return ""

        finally:

            if temp_file and os.path.exists(temp_file):

                try:
                    os.remove(temp_file)

                except Exception:
                    pass