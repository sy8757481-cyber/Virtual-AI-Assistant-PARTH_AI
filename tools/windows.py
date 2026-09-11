"""PARTH AI — Windows Control Module. Fixed commands only."""

import subprocess
import pyautogui
from utils.logger import log_info, log_error


class WindowsController:
    def _open(self, executable, name):
        try:
            subprocess.Popen([executable])
            log_info(f"{name} Opened")
        except Exception as e:
            log_error(f"{name} Error : {e}")
            raise

    def open_notepad(self):
        self._open("notepad.exe", "Notepad")

    def open_calculator(self):
        self._open("calc.exe", "Calculator")

    def open_cmd(self):
        self._open("cmd.exe", "CMD")

    def open_paint(self):
        self._open("mspaint.exe", "Paint")

    def open_explorer(self):
        self._open("explorer.exe", "File Explorer")

    def take_screenshot(self, filename="screenshot.png"):
        try:
            image = pyautogui.screenshot()
            image.save(filename)
            log_info(f"Screenshot Saved : {filename}")
        except Exception as e:
            log_error(f"Screenshot Error : {e}")
            raise

    def lock_pc(self):
        try:
            # Windows API reports failure; no shell or user-supplied command.
            import ctypes
            if not ctypes.windll.user32.LockWorkStation():
                raise OSError("Windows rejected the lock request.")
            log_info("PC Lock Requested")
        except Exception as e:
            log_error(f"PC Lock Error : {e}")
            raise
