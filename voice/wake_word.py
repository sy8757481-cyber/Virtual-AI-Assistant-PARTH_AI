"""PARTH AI — Wake Word Module. Existing reset/release timing preserved."""

import time
import pyaudio
import numpy as np
import openwakeword
from openwakeword.model import Model
from utils.logger import log_info, log_error


class WakeWord:
    def __init__(self):
        try:
            openwakeword.utils.download_models()
            self.model = Model(inference_framework="onnx")
            self.available_models = list(self.model.models.keys())
            self.running = False
            self.wake_word = "hey_jarvis"
            if self.wake_word not in self.available_models:
                raise RuntimeError("The hey_jarvis wake-word model is unavailable.")
            log_info(f"Wake Word Loaded : {self.available_models}")
            print(f"Wake Word Model Loaded : {self.available_models}")
        except Exception as e:
            log_error(f"Wake Word Init Error : {e}")
            raise

    def available_wake_words(self):
        return self.available_models

    def is_loaded(self):
        return self.model is not None

    def reset_model(self):
        """Re-create the model to remove previous audio/prediction state."""
        try:
            self.model = Model(inference_framework="onnx")
            log_info("Wake Word Model Reset Successfully.")
        except Exception as e:
            log_error(f"Wake Word Model Reset Error : {e}")
            # Do not reuse stale predictions if the reset failed.
            raise

    def start_listening(self):
        self.running = True
        CHUNK = 1280
        RATE = 16000
        audio = None
        stream = None
        try:
            self.reset_model()
            time.sleep(0.5)
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt16, channels=1, rate=RATE,
                input=True, frames_per_buffer=CHUNK,
            )
            # Preserve the existing stale-audio discard on every wake session.
            for _ in range(5):
                stream.read(CHUNK, exception_on_overflow=False)
            while self.running:
                frame = np.frombuffer(
                    stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16,
                )
                prediction = self.model.predict(frame)
                # Other bundled words (e.g. "weather") must not wake PARTH.
                score = float(prediction.get(self.wake_word, 0.0))
                if score >= 0.75:
                    print(f"\n✅ {self.wake_word} detected ({score:.2f})")
                    log_info(f"Wake Word Detected : {self.wake_word} ({score:.2f})")
                    self.running = False
                    return True
            return False
        except Exception as e:
            log_error(f"Wake Word Listening Error : {e}")
            return False
        finally:
            if stream is not None:
                try:
                    stream.stop_stream()
                except Exception:
                    pass
                try:
                    stream.close()
                except Exception:
                    pass
            if audio is not None:
                try:
                    audio.terminate()
                except Exception:
                    pass
            self.running = False
            time.sleep(0.8)

    def stop(self):
        self.running = False
