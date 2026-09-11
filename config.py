# ==========================================
# PARTH AI CONFIGURATION
# ==========================================

# Project Information
PROJECT_NAME = "Parth AI"
VERSION = "1.0.0"

# Voice Settings (used by subprocess TTS)
VOICE_RATE = 170
VOICE_VOLUME = 1.0

# Browser Settings
DEFAULT_BROWSER = "chrome"

# Local LLM — matches the current lightweight LLM module
LLM_PROVIDER = "ollama"
LLM_MODEL = "qwen2.5:1.5b"

# Current ONNX model key. Spoken wake phrase: "Hey Jarvis".
WAKE_WORD = "hey_jarvis"

# Memory (reserved for existing/future consumers)
MEMORY_DATABASE = "data/memory.db"

# Logging
LOG_FILE = "logs/parth.log"

# Assistant
ASSISTANT_NAME = "Parth"

# Screen
SCREENSHOT_FOLDER = "assets"

# Time
TIMEZONE = "Asia/Kolkata"