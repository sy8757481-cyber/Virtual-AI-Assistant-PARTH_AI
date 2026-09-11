"""PARTH AI — Planner Module (Version 1.1)."""

from utils.logger import log_info, log_error


class Planner:
    def __init__(self):
        log_info("Planner Initialized Successfully.")

    def create_plan(self, command: dict):
        """Keep the existing one-command, one-step plan."""
        try:
            if not isinstance(command, dict):
                return []
            # Reject malformed model output instead of calling strip on None.
            values = [command.get(key, "") for key in ("tool", "action", "query")]
            if not all(isinstance(value, str) for value in values):
                log_error("Planner: tool, action and query must be strings.")
                return []
            tool, action, query = (value.strip() for value in values)
            if not tool or not action:
                return []
            return [{"tool": tool, "action": action, "query": query}]
        except Exception as e:
            log_error(f"Planner Error : {e}")
            return []

    def print_plan(self, plan):
        try:
            print("\n========== EXECUTION PLAN ==========\n")
            if not plan:
                print("No Steps")
            else:
                for index, step in enumerate(plan, start=1):
                    print(f"{index}. {step['tool']} -> {step['action']} -> {step['query']}")
            print("\n====================================\n")
        except Exception as e:
            log_error(f"Planner Print Error : {e}")
