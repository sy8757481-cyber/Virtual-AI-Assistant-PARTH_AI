"""
==========================================
PARTH AI
LLM Module (Version 5)
==========================================
"""

import ollama

from brain.parser import Parser

from utils.logger import log_info, log_error


class LLM:

    def __init__(self):

        self.model = "qwen2.5:1.5b"

        self.parser = Parser()

        self.system_prompt = """
You are PARTH AI.

You convert user requests into ONE JSON object.

Available tools:

Browser
- google_search
- youtube_search
- open_url

Windows
- open_notepad
- open_calculator
- open_cmd
- open_paint
- open_explorer
- take_screenshot
- lock_pc

Chat
- reply

Rules:

1. Return ONLY JSON.
2. Never explain.
3. Never use markdown.
4. query must always be a string.

Output format:

{
    "tool":"",
    "action":"",
    "query":""
}

Examples:

User:
Open calculator

Output:
{
    "tool":"windows",
    "action":"open_calculator",
    "query":""
}

User:
Play Arijit Singh songs

Output:
{
    "tool":"browser",
    "action":"youtube_search",
    "query":"Arijit Singh songs"
}

User:
Search Python tutorial

Output:
{
    "tool":"browser",
    "action":"google_search",
    "query":"Python tutorial"
}

User:
What is Artificial Intelligence?

Output:
{
    "tool":"chat",
    "action":"reply",
    "query":"Artificial Intelligence is the simulation of human intelligence by machines."
}
"""

        log_info("LLM Initialized Successfully.")

    def process(self, user_input: str):

        try:

            response = ollama.chat(

                model=self.model,

                messages=[

                    {
                        "role": "system",
                        "content": self.system_prompt
                    },

                    {
                        "role": "user",
                        "content": user_input
                    }

                ]

            )

            reply = response["message"]["content"]

            print("\n========== RAW LLM RESPONSE ==========")
            print(reply)
            print("======================================\n")

            log_info(f"RAW LLM : {reply}")

            command = self.parser.parse(reply)

            log_info(f"PARSED : {command}")

            return command


        except Exception as e:

            print("\n========== LLM ERROR ==========")

            print(type(e).__name__)

            print(e)

            print("===============================\n")

            log_error(f"LLM Error : {e}")

            return {

                "tool": "chat",

                "action": "reply",

                "query": "Sorry, something went wrong."

            }