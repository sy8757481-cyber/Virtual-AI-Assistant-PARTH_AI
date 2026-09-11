"""PARTH AI — Text To Speech Module. Speech runs in a fresh subprocess."""

import json
import subprocess
import sys
import threading
from types import SimpleNamespace
from config import VOICE_RATE, VOICE_VOLUME
from utils.logger import log_info, log_error

# Constant program text. User speech is passed through stdin as JSON, never
# interpolated into Python code or a shell command.
_TTS_SCRIPT = r'''
import json
import sys
import pyttsx3

request = json.load(sys.stdin)
engine = pyttsx3.init()
try:
    voices = engine.getProperty("voices") or []
    if request["action"] == "voices":
        print(json.dumps([{"id": v.id, "name": v.name} for v in voices]))
    else:
        engine.setProperty("rate", request["rate"])
        engine.setProperty("volume", request["volume"])
        index = request["voice_index"]
        if 0 <= index < len(voices):
            engine.setProperty("voice", voices[index].id)
        engine.say(request["text"])
        engine.runAndWait()
finally:
    engine.stop()
'''


class TextToSpeech:
    def __init__(self):
        self.rate = int(VOICE_RATE)
        self.volume = max(0.0, min(1.0, float(VOICE_VOLUME)))
        self.voice_index = 0
        self.voices = []
        self._process = None
        self._speak_lock = threading.Lock()
        # No persistent pyttsx3 engine in the microphone/listener process.
        log_info("Text To Speech Initialized Successfully (subprocess mode).")

    def _run(self, payload, timeout):
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        process = subprocess.Popen(
            [sys.executable, "-c", _TTS_SCRIPT],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            creationflags=creationflags,
        )
        self._process = process
        try:
            stdout, stderr = process.communicate(json.dumps(payload), timeout=timeout)
            if process.returncode != 0:
                raise RuntimeError(stderr.strip() or "Speech subprocess stopped.")
            return stdout
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            raise RuntimeError("Speech subprocess timed out.")
        finally:
            if self._process is process:
                self._process = None

    def speak(self, text: str):
        if text is None:
            return False
        text = str(text).strip()
        if not text:
            return False
        try:
            with self._speak_lock:
                log_info(f"Assistant Said : {text}")
                self._run({
                    "action": "speak",
                    "text": text,
                    "rate": self.rate,
                    "volume": self.volume,
                    "voice_index": self.voice_index,
                }, timeout=max(30, min(300, len(text) // 5 + 20)))
            return True
        except Exception as e:
            log_error(f"TTS Speak Error : {e}")
            return False

    def stop(self):
        try:
            process = self._process
            if process is not None and process.poll() is None:
                process.terminate()
            log_info("Speech Stopped")
        except Exception as e:
            log_error(f"TTS Stop Error : {e}")

    def set_voice(self, index=0):
        try:
            with self._speak_lock:
                if not self.voices:
                    output = self._run({"action": "voices"}, timeout=20)
                    self.voices = [SimpleNamespace(**v) for v in json.loads(output)]
                if isinstance(index, int) and 0 <= index < len(self.voices):
                    self.voice_index = index
                    log_info(f"Voice Changed : {index}")
                    return True
            return False
        except Exception as e:
            log_error(f"Voice Change Error : {e}")
            return False
