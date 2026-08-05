"""
==========================================
PARTH AI
Agent Module (Version 4)
==========================================
"""

from brain.llm import LLM
from brain.planner import Planner

from tools.browser import Browser
from tools.windows import WindowsController

from utils.logger import log_info, log_error


class Agent:

    def __init__(self):

        self.llm = LLM()
        self.planner = Planner()

        self.browser = Browser()
        self.windows = WindowsController()

        self.browser.start()

        log_info("Agent Initialized Successfully.")

    def execute(self, user_input: str):

        try:

            # -------------------------
            # Step 1 : LLM
            # -------------------------

            command = self.llm.process(user_input)

            # -------------------------
            # Step 2 : Planner
            # -------------------------

            plan = self.planner.create_plan(command)

            self.planner.print_plan(plan)

            # -------------------------
            # Step 3 : Execute Plan
            # -------------------------

            responses = []

            for step in plan:

                result = self.execute_step(step)

                if result:
                    responses.append(result)

            return " ".join(responses)

        except Exception as e:

            log_error(f"Agent Error : {e}")

            return "Sorry, something went wrong."

    def execute_step(self, step: dict):

        tool = step["tool"]
        action = step["action"]
        query = step["query"]

        # ---------------------------------
        # Browser
        # ---------------------------------

        if tool == "browser":

            if action == "google_search":

                self.browser.google_search(query)

                return f"Searching Google for {query}"

            elif action == "youtube_search":

                self.browser.youtube_search(query)

                return f"Playing {query} on YouTube"

            elif action == "open_url":

                if query and not query.startswith("http"):
                    query = "https://" + query

                self.browser.open_url(query)

                return f"Opening {query}"

        # ---------------------------------
        # Windows
        # ---------------------------------

        elif tool == "windows":

            if hasattr(self.windows, action):

                getattr(self.windows, action)()

                return action.replace("_", " ").title()

        # ---------------------------------
        # Chat
        # ---------------------------------

        elif tool == "chat":

            print(f"\n🤖 PARTH : {query}\n")

            return query

        # ---------------------------------
        # Unknown
        # ---------------------------------

        message = "Sorry, I don't understand that command."

        print(message)

        return message

    def close(self):

        try:

            self.browser.close()

        except Exception as e:

            log_error(e)