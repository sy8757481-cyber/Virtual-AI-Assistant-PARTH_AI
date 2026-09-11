"""PARTH AI — Agent Module (Version 6.1)."""

from brain.llm import LLM
from brain.planner import Planner
from tools.browser import Browser
from tools.windows import WindowsController
from tools.calculator import Calculator
from utils.logger import log_info, log_error


class Agent:
    def __init__(self):
        self.llm = LLM()
        self.planner = Planner()
        self.browser = Browser()
        self.windows = WindowsController()
        self.calculator = Calculator()
        # A browser startup failure should not disable calculator/Windows tasks.
        try:
            self.browser.start()
        except Exception as e:
            log_error(f"Browser Startup Error : {e}")
        log_info("Agent Initialized Successfully.")

    def execute(self, user_input: str):
        try:
            if not isinstance(user_input, str) or not user_input.strip():
                return ""
            command = self.llm.process(user_input)
            plan = self.planner.create_plan(command)
            self.planner.print_plan(plan)
            if not plan:
                return "Sorry sir, I couldn't understand that request."
            responses = []
            for step in plan:
                result = self.execute_step(step)
                if result:
                    responses.append(str(result))
            return " ".join(responses)
        except Exception as e:
            log_error(f"Agent Error : {e}")
            return "Sorry sir, something went wrong."

    def execute_step(self, step: dict):
        try:
            if not isinstance(step, dict):
                return "Sorry, I don't understand that command."
            values = [step.get(key, "") for key in ("tool", "action", "query")]
            if not all(isinstance(value, str) for value in values):
                return "Sorry, I don't understand that command."
            tool, action, query = (value.strip() for value in values)

            if tool == "calculator" and action == "calculate":
                try:
                    result = self.calculator.calculate(query)
                    message = f"The answer is {result}."
                    print(f"\n🤖 PARTH : {message}\n")
                    log_info(f"Calculator Result : {result}")
                    return message
                except Exception as e:
                    log_error(f"Calculator Error : {e}")
                    return "Sorry sir, I couldn't calculate that."

            if tool == "browser":
                # An explicit allowlist prevents arbitrary attribute dispatch.
                controls = {
                    "play_video": (self.browser.play_video, "Music resumed."),
                    "pause_video": (self.browser.pause_video, "Music paused."),
                    "stop_video": (self.browser.stop_video, "Music stopped."),
                    "next_video": (self.browser.next_video, "Playing the next video."),
                    "previous_video": (self.browser.previous_video, "Playing the previous video."),
                    "volume_up": (self.browser.volume_up, "Volume increased."),
                    "volume_down": (self.browser.volume_down, "Volume decreased."),
                    "mute": (self.browser.mute, "Muted."),
                    "unmute": (self.browser.unmute, "Unmuted."),
                }
                if action in controls:
                    handler, message = controls[action]
                    handler()  # Updated Browser raises if the action fails.
                    return message
                if action == "google_search":
                    self.browser.google_search(query)
                    return f"Searching Google for {query}."
                if action == "youtube_search":
                    self.browser.youtube_search(query)
                    return f"Playing {query} on YouTube."
                if action == "open_url":
                    self.browser.open_url(query)
                    return "Page opened."

            if tool == "windows":
                actions = {
                    "open_notepad": "Notepad opened.",
                    "open_calculator": "Calculator opened.",
                    "open_cmd": "Command Prompt opened.",
                    "open_paint": "Paint opened.",
                    "open_explorer": "File Explorer opened.",
                    "take_screenshot": "Screenshot saved.",
                    "lock_pc": "Computer locked.",
                }
                if action in actions:
                    getattr(self.windows, action)()
                    return actions[action]

            if tool == "chat" and action == "reply":
                print(f"\n🤖 PARTH : {query}\n")
                return query
            return "Sorry, I don't understand that command."
        except Exception as e:
            log_error(f"Execute Step Error : {e}")
            # Browser deliberately exposes only its own safe, useful messages.
            from tools.browser import BrowserActionError
            if isinstance(e, BrowserActionError):
                return str(e)
            return "Sorry sir, I couldn't complete that task."

    def close(self):
        try:
            if self.browser:
                self.browser.close()
        except Exception as e:
            log_error(f"Agent Close Error : {e}")
