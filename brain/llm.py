"""PARTH AI — LLM Module (Version 7.2)."""

import re
import ollama
from brain.parser import Parser
from utils.logger import log_info, log_error


class LLM:
    def __init__(self):
        self.model = "qwen2.5:1.5b"
        self.parser = Parser()
        self.system_prompt = '''
You are PARTH AI. Convert the user's request into ONE JSON object.
Return ONLY JSON, never markdown or an explanation outside JSON.
The format is {"tool":"", "action":"", "query":""}.
All three values must be strings. Choose only an action listed below.

Calculator: calculate
Browser: google_search, youtube_search, open_url, play_video, pause_video,
stop_video, next_video, previous_video, volume_up, volume_down, mute, unmute
Windows: open_notepad, open_calculator, open_cmd, open_paint, open_explorer,
take_screenshot, lock_pc
Chat: reply

For mathematics choose calculator/calculate and put the expression in query.
Do not calculate the answer yourself.
For opening the Windows calculator choose windows/open_calculator.
For playing a named song choose browser/youtube_search with the title in query.
For resuming the current video choose browser/play_video with an empty query.
For other YouTube controls and Windows actions use an empty query.
For general questions choose chat/reply and put the answer in query.
Do not invent tools or claim that an action has already been performed.

Examples:
Calculate 25 times 8 -> {"tool":"calculator","action":"calculate","query":"25 * 8"}
Open calculator -> {"tool":"windows","action":"open_calculator","query":""}
Play Arijit Singh songs -> {"tool":"browser","action":"youtube_search","query":"Arijit Singh songs"}
Play Aadat -> {"tool":"browser","action":"youtube_search","query":"Aadat"}
Pause the music -> {"tool":"browser","action":"pause_video","query":""}
Resume music -> {"tool":"browser","action":"play_video","query":""}
Stop the song -> {"tool":"browser","action":"stop_video","query":""}
Play next song -> {"tool":"browser","action":"next_video","query":""}
Go to previous song -> {"tool":"browser","action":"previous_video","query":""}
Increase volume -> {"tool":"browser","action":"volume_up","query":""}
Decrease volume -> {"tool":"browser","action":"volume_down","query":""}
Mute -> {"tool":"browser","action":"mute","query":""}
Unmute -> {"tool":"browser","action":"unmute","query":""}
Search Python tutorial -> {"tool":"browser","action":"google_search","query":"Python tutorial"}
What is Artificial Intelligence? -> {"tool":"chat","action":"reply","query":"Artificial Intelligence is the simulation of human intelligence by machines."}
'''
        log_info("LLM Initialized Successfully.")

    @staticmethod
    def _normalize(user_input):
        text = re.sub(r"\s+", " ", user_input.lower()).strip(" .!?,")
        # Optional politeness/assistant name, without modifying named searches.
        text = re.sub(r"^(?:(?:hey )?parth[, ]+|please )+", "", text)
        text = re.sub(r"(?:[, ]+(?:please|parth))+$", "", text)
        return text.strip(" .!?,")

    def detect_calculation(self, user_input: str):
        if not isinstance(user_input, str):
            return None
        expression = user_input.lower().strip()
        expression = re.sub(r"^(calculate|what is|what's|tell me)\s+", "", expression)
        replacements = (
            (r"\bmultiplied by\b", "*"),
            (r"\bdivided by\b|\bdivide by\b", "/"),
            (r"\bto the power of\b|\bpower of\b|\bpower\b", "**"),
            (r"\bplus\b", "+"),
            (r"\bminus\b", "-"),
            (r"\btimes\b", "*"),
            (r"\bmodulo\b|\bmod\b", "%"),
        )
        for pattern, replacement in replacements:
            expression = re.sub(pattern, replacement, expression)
        expression = expression.replace("×", "*").replace("÷", "/").replace("^", "**")
        expression = re.sub(r"(\d+(?:\.\d+)?)\s+squared\b", r"(\1**2)", expression)
        expression = re.sub(r"(\d+(?:\.\d+)?)\s+cubed\b", r"(\1**3)", expression)
        expression = expression.strip().rstrip("?!").strip()
        # A sentence-ending period, but preserve leading decimal points.
        if expression.endswith("."):
            expression = expression[:-1].rstrip()
        # Only arithmetic text takes the shortcut. Sentences containing e.g.
        # "times" or "model" must not accidentally become calculations.
        if (re.fullmatch(r"[\d\s.()+*/%\-]+", expression, flags=re.ASCII)
                and re.search(r"[0-9]", expression)
                and re.search(r"[+*/%\-]", expression)):
            return expression
        return None

    def detect_youtube_control(self, user_input: str):
        if not isinstance(user_input, str):
            return None
        text = self._normalize(user_input)
        groups = {
            "pause_video": (
                "pause", "pause music", "pause the music", "pause song",
                "pause the song", "pause video", "pause the video",
            ),
            "play_video": (
                "resume", "resume music", "resume the music", "resume song",
                "resume the song", "resume video", "resume the video", "continue",
                "continue music", "continue song", "continue video", "play",
                "play music", "play the music", "play song", "play the song",
                "play video", "play the video", "continue playing",
            ),
            "stop_video": (
                "stop music", "stop the music", "stop song", "stop the song",
                "stop video", "stop the video", "stop playing", "stop the music playing",
            ),
            "next_video": (
                "next", "next song", "next the song", "next video",
                "next song please", "play next", "play next song",
                "play the next song", "play next video", "play the next video",
            ),
            "previous_video": (
                "previous", "previous song", "previous video", "previous song please",
                "play previous", "play previous song", "play the previous song",
                "go to previous song", "play previous video", "play the previous video",
            ),
            "volume_up": (
                "volume up", "increase volume", "increase the volume",
                "turn up volume", "turn up the volume", "make it louder", "louder",
            ),
            "volume_down": (
                "volume down", "decrease volume", "decrease the volume",
                "turn down volume", "turn down the volume", "make it quieter", "quieter",
            ),
            "mute": ("mute", "mute music", "mute the music", "mute video", "mute the video"),
            "unmute": ("unmute", "unmute music", "unmute the music", "unmute video", "unmute the video"),
        }
        for action, phrases in groups.items():
            if text in phrases:
                return {"tool": "browser", "action": action, "query": ""}
        return None

    def detect_windows_command(self, user_input: str):
        """Route only complete, known commands to existing Windows actions."""
        if not isinstance(user_input, str):
            return None
        text = self._normalize(user_input)
        text = re.sub(r"^(?:can you|could you|would you)\s+", "", text)
        text = self._normalize(text)
        applications = {
            "notepad": "open_notepad",
            "note pad": "open_notepad",
            "calculator": "open_calculator",
            "calc": "open_calculator",
            "cmd": "open_cmd",
            "command prompt": "open_cmd",
            "paint": "open_paint",
            "ms paint": "open_paint",
            "microsoft paint": "open_paint",
            "explorer": "open_explorer",
            "file explorer": "open_explorer",
            "windows explorer": "open_explorer",
        }
        match = re.fullmatch(r"(?:open|launch|start) (?:the )?(.+)", text)
        action = applications.get(match.group(1)) if match else None
        if text in {
            "take screenshot", "take a screenshot", "take the screenshot",
            "capture screenshot", "capture a screenshot", "screenshot",
        }:
            action = "take_screenshot"
        elif text in {
            "lock pc", "lock my pc", "lock the pc", "lock your pc",
            "lock computer", "lock my computer", "lock the computer",
            "lock screen", "lock my screen", "lock the screen",
        }:
            action = "lock_pc"
        if action:
            return {"tool": "windows", "action": action, "query": ""}
        return None

    def _ollama_failure(self, error):
        """Return one useful spoken response; retain details in the log."""
        log_error(f"LLM Error : {error}")
        if isinstance(error, ConnectionError):
            message = (
                "I couldn't connect to Ollama. Please start Ollama and try again. "
                "You can still use basic Windows commands, calculations, and YouTube controls."
            )
        elif getattr(error, "status_code", None) == 404:
            message = (
                "Ollama could not find the requested model or endpoint. "
                f"Please check that {self.model} is installed in Ollama."
            )
        else:
            message = "Ollama couldn't complete that request. Please check the PARTH log."
        return {"tool": "chat", "action": "reply", "query": message}

    def process(self, user_input: str):
        try:
            if not isinstance(user_input, str) or not user_input.strip():
                return {}
            command = self.detect_windows_command(user_input)
            if command:
                log_info(f"Direct Windows Command : {command}")
                return command
            command = self.detect_youtube_control(user_input)
            if command:
                log_info(f"Direct YouTube Control : {command}")
                return command
            expression = self.detect_calculation(user_input)
            if expression:
                command = {"tool": "calculator", "action": "calculate", "query": expression}
                log_info(f"Direct Calculator : {command}")
                return command
            # Deterministic named-song shortcut, after current-video controls.
            # More complex requests still go to the existing local model.
            match = re.fullmatch(r"(?:please\s+)?play\s+(.+)", user_input.strip(), flags=re.I)
            if match:
                query = match.group(1).strip().rstrip(".!?")
                if query and not re.search(r"\b(?:and then|then)\b", query, flags=re.I):
                    query = re.sub(r"\s+on youtube$", "", query, flags=re.I).strip()
                    return {"tool": "browser", "action": "youtube_search", "query": query}
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": user_input},
                    ],
                    format="json",
                    options={"temperature": 0},
                )
            except Exception as e:
                return self._ollama_failure(e)
            reply = response["message"]["content"]
            print(f"\n========== RAW LLM RESPONSE ==========\n{reply}\n======================================\n")
            log_info(f"RAW LLM : {reply}")
            command = self.parser.parse(reply)
            log_info(f"PARSED : {command}")
            return command
        except Exception as e:
            log_error(f"LLM Error : {e}")
            return {"tool": "chat", "action": "reply", "query": "Sorry, something went wrong."}
