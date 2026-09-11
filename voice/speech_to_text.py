"""PARTH AI — Speech To Text Module. Existing noise protections retained."""

import os
import re
import tempfile
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
from utils.logger import log_info, log_error


class SpeechToText:
    def __init__(self):
        try:
            self.sample_rate = 16000
            self.energy_threshold = 450
            self.model = WhisperModel("tiny", device="cpu", compute_type="int8")
            log_info("Speech To Text Initialized Successfully.")
        except Exception as e:
            log_error(f"Speech To Text Initialization Error : {e}")
            raise

    def _has_speech(self, audio):
        try:
            if audio is None or len(audio) == 0:
                return False
            samples = audio.astype(np.float32).flatten()
            if samples.size == 0 or not np.isfinite(samples).all():
                return False
            rms = np.sqrt(np.mean(samples ** 2))
            log_info(f"Audio RMS : {rms:.2f}")
            if rms < self.energy_threshold:
                return False
            frame_size = int(0.03 * self.sample_rate)
            if frame_size <= 0:
                return False
            total_frames = 0
            active_frames = 0
            for start in range(0, len(samples), frame_size):
                frame = samples[start:start + frame_size]
                if len(frame) == 0:
                    continue
                frame_rms = np.sqrt(np.mean(frame ** 2))
                total_frames += 1
                if frame_rms >= self.energy_threshold:
                    active_frames += 1
            if total_frames == 0:
                return False
            speech_ratio = active_frames / total_frames
            log_info(f"Speech Activity : {speech_ratio:.2f}")
            return speech_ratio >= 0.05
        except Exception as e:
            log_error(f"Speech Detection Error : {e}")
            return False

    def listen(self, duration=5):
        temp_file = None
        try:
            print("\n🎤 Listening...")
            audio = sd.rec(
                int(duration * self.sample_rate), samplerate=self.sample_rate,
                channels=1, dtype="int16",
            )
            sd.wait()
            if not self._has_speech(audio):
                print("🔇 No clear speech detected.")
                return ""
            # Close the temporary handle before scipy reopens it on Windows.
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as file:
                temp_file = file.name
            write(temp_file, self.sample_rate, audio)
            segments, info = self.model.transcribe(
                temp_file, language="en", task="transcribe", vad_filter=True,
                vad_parameters={"min_silence_duration_ms": 500}, beam_size=5,
                temperature=0, condition_on_previous_text=False,
            )
            text_parts = []
            for segment in segments:
                segment_text = segment.text.strip()
                if not segment_text:
                    continue
                if segment.no_speech_prob > 0.60:
                    log_info(f"Ignored probable silence: {segment_text}")
                    continue
                text_parts.append(segment_text)
            text = " ".join(text_parts).strip()
            if not self._is_valid_text(text):
                print("🔇 Ignored unclear audio.")
                return ""
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
                except Exception as e:
                    log_error(f"Temporary Audio Cleanup Error : {e}")

    def _is_valid_text(self, text):
        if not isinstance(text, str) or not text.strip():
            return False
        # Match hallucinations even when Whisper adds punctuation: "You."
        normalized = re.sub(r"[^\w\s]", "", text.lower())
        normalized = " ".join(normalized.split())
        hallucinations = {
            "you", "thank you", "thanks for watching", "thank you for watching",
            "bye", "subscribe", "please subscribe", "you guys", "okay", "ok",
        }
        # "goodbye" is a real shutdown command; acoustic/VAD checks still apply.
        if normalized in hallucinations:
            log_info(f"Ignored hallucination: {text}")
            return False
        return len(normalized) >= 2
