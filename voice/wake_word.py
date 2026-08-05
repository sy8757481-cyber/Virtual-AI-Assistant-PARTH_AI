# Add inside WakeWord class

"""
==========================================
PARTH AI
Wake Word Module
==========================================
"""
import pyaudio
import numpy as np
import openwakeword
import sounddevice as sd
import numpy as np

from openwakeword.model import Model

from utils.logger import log_info, log_error


class WakeWord:

    def __init__(self):

        try:

            openwakeword.utils.download_models()

            self.model = Model(
                inference_framework="onnx"
            )

            self.available_models = list(
                self.model.models.keys()
            )

            self.running = False

            log_info(
                f"Wake Word Loaded : {self.available_models}"
            )

        except Exception as e:

            log_error(f"Wake Word Init Error : {e}")

            raise

    def available_wake_words(self):

        return self.available_models

    def is_loaded(self):

        return self.model is not None



    def start_listening(self):

        self.running = True

        CHUNK = 1280
        RATE = 16000

        audio = pyaudio.PyAudio()

        stream = audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        print("🎤 Waiting for wake word...")

        while self.running:

            frame = np.frombuffer(
                stream.read(CHUNK, exception_on_overflow=False),
                dtype=np.int16
            )

            prediction = self.model.predict(frame)

            for wake_word, score in prediction.items():

                if score >= 0.5:
                    print(f"\n✅ {wake_word} detected ({score:.2f})")

                    stream.stop_stream()
                    stream.close()
                    audio.terminate()

                    return True

    def stop(self):

        self.running = False