"""
==========================================
PARTH AI
Parser Module (Version 2.1)
==========================================
"""

import json
import re

from utils.logger import log_info, log_error


class Parser:
    def __init__(self):
        log_info("Parser Initialized Successfully.")

    def parse(self, text: str):
        try:
            if not isinstance(text, str) or not text.strip():
                return self.default_response()

            text = text.strip()
            # Remove only an outer fence. Preserve backticks inside query text.
            fence = re.fullmatch(
                r"```(?:json)?\s*([\s\S]*?)\s*```", text, flags=re.IGNORECASE
            )
            if fence:
                text = fence.group(1).strip()

            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                # Accept one object surrounded by model prose. raw_decode
                # understands nested braces and braces inside quoted strings.
                # Reject multiple objects rather than choosing an action.
                decoder = json.JSONDecoder()
                objects = []
                position = 0
                while True:
                    start = text.find("{", position)
                    if start == -1:
                        break
                    value, end = decoder.raw_decode(text, start)
                    objects.append(value)
                    position = end
                if len(objects) != 1:
                    raise ValueError("Expected exactly one JSON command object.")
                data = objects[0]

            if not isinstance(data, dict):
                raise ValueError("The command must be a JSON object.")

            values = [data.get(key, "") for key in ("tool", "action", "query")]
            if not all(isinstance(value, str) for value in values):
                raise ValueError("tool, action and query must be strings.")

            tool, action, query = (value.strip() for value in values)
            if not tool or not action:
                raise ValueError("tool and action must not be empty.")

            command = {"tool": tool, "action": action, "query": query}
            log_info(f"Parser Output : {command}")
            return command

        except Exception as e:
            log_error(f"Parser Error : {e}")
            return self.default_response()

    @staticmethod
    def default_response():
        return {
            "tool": "chat",
            "action": "reply",
            "query": "Sorry, something went wrong.",
        }
