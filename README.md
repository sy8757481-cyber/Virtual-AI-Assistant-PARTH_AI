# 🤖 PARTH AI — Windows Voice Assistant

PARTH AI is a Python-based intelligent voice assistant for Windows that combines voice recognition, a local LLM, browser automation, and Windows automation to execute commands through natural language.

The project is designed around a modular AI-agent architecture where voice commands are converted into structured actions and executed using specialized tools.

## ✨ Features

- 🎙️ Voice command recognition
- 🔊 Text-to-Speech responses
- 🗣️ Wake word detection using **"Hey Jarvis"**
- 😴 Sleep and wake mode
- 🧠 Local AI processing using **Ollama + Qwen2.5**
- 🌐 Google search automation
- ▶️ YouTube search and playback
- ⏯️ YouTube Play / Pause / Resume / Stop
- ⏭️ Next and Previous video controls
- 🔊 YouTube volume control
- 🔇 Mute / Unmute
- 🧮 Voice-controlled calculator
- 🪟 Windows application automation
- 📸 Screenshot support
- 🔒 PC locking
- 🛡️ Noise and silence filtering for voice recognition
- 🔧 Modular tool-based architecture

## 🧠 Architecture

```text
Wake Word
    ↓
Speech To Text
    ↓
Local LLM
    ↓
Parser
    ↓
Planner
    ↓
Agent
    ↓
Tools
    ↓
Task Execution
    ↓
Text To Speech
```

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Language | Python |
| Local LLM | Ollama |
| AI Model | Qwen2.5:1.5b |
| Speech Recognition | Faster-Whisper |
| Wake Word | OpenWakeWord |
| Text-to-Speech | pyttsx3 |
| Browser Automation | Playwright |
| Audio Input | sounddevice / PyAudio |
| AI Inference | ONNX Runtime |
| IDE | PyCharm |
| Platform | Windows |

## 📂 Project Structure

```text
PARTH/
│
├── brain/
│   ├── agent.py
│   ├── llm.py
│   ├── parser.py
│   └── planner.py
│
├── tools/
│   ├── browser.py
│   ├── calculator.py
│   ├── chrome.py
│   └── windows.py
│
├── voice/
│   ├── speech_to_text.py
│   ├── text_to_speech.py
│   └── wake_word.py
│
├── utils/
│   └── logger.py
│
├── tests/
│
├── config.py
├── main.py
├── requirements.txt
└── README.md
```

## 🎤 Example Commands

PARTH AI can understand commands such as:

```text
Hey Jarvis

Open calculator
Open Notepad
Open Command Prompt

Search Python tutorials on Google

Play Aadat song
Pause music
Resume music
Next song
Previous song
Volume up
Volume down
Mute
Unmute
Stop music

What is 25 times 8?

Take a screenshot
Open File Explorer
Lock my PC

Go to sleep
Shutdown
```

## 🧮 Calculator

PARTH contains a dedicated calculator tool that safely evaluates mathematical expressions using Python's AST instead of unsafe `eval()`.

Examples:

```text
2 + 2
25 times 8
100 divided by 4
10 modulo 3
2 power 10
```

Example response:

```text
The answer is 200.
```

## 🌐 Browser Automation

PARTH uses Playwright for browser automation.

Current browser capabilities include:

- Google Search
- Open URLs
- YouTube Search
- YouTube Playback
- Play / Pause
- Stop
- Next / Previous
- Volume Up / Down
- Mute / Unmute
- Scrolling
- Tab management
- Back / Forward
- Refresh
- Page reading

## 🪟 Windows Automation

PARTH can currently perform Windows actions such as:

```text
Open Notepad
Open Calculator
Open Command Prompt
Open Paint
Open File Explorer
Take Screenshot
Lock PC
```

## 🧠 Local AI

PARTH runs its AI model locally using Ollama.

Current model:

```text
qwen2.5:1.5b
```

Using a local model reduces dependency on paid cloud APIs and allows the assistant to run on modest hardware.

The LLM converts natural-language requests into structured commands:

```json
{
  "tool": "browser",
  "action": "youtube_search",
  "query": "Aadat song"
}
```

The Agent then sends the action to the appropriate tool.

## 🎙️ Speech Recognition

Speech recognition is powered by Faster-Whisper using the Tiny model with CPU INT8 inference.

The voice pipeline includes:

- Silence detection
- Audio energy filtering
- Voice Activity Detection
- Whisper hallucination filtering
- Background-noise protection

This prevents random background noise from unnecessarily triggering AI actions.

## 🚀 Running PARTH AI

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd PARTH
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate it on Windows

```powershell
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Install Playwright browser support

```bash
playwright install
```

### 6. Install Ollama

Install Ollama and download the model:

```bash
ollama pull qwen2.5:1.5b
```

### 7. Start PARTH AI

```bash
python main.py
```

Then say:

```text
Hey Jarvis
```

PARTH will respond and start listening for commands.

## 🔮 Future Improvements

Planned improvements include:

- Multi-step AI planning
- Better conversational memory
- More Windows automation
- File and folder management
- Email automation
- Calendar integration
- Advanced browser automation
- Custom PARTH wake word
- Improved natural-language understanding
- More AI tools and integrations

## 🔐 Security

PARTH is designed with safety in mind.

For example, mathematical expressions are evaluated using a restricted AST-based calculator rather than Python's unrestricted `eval()`.

Sensitive files such as `.env` should never be committed to the repository.

## 📌 Project Status

🚧 **Active Development**

PARTH AI is currently under development and new tools, automation capabilities, and AI-agent features are being added progressively.

## 👨‍💻 Author

**Suman Kumar**

B.Tech — Computer Science & Engineering

---

⭐ If you find PARTH AI interesting, consider starring the repository.