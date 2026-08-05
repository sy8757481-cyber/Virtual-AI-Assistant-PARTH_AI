"""
==========================================
PARTH AI
Windows Control Module
==========================================
"""

import os
import subprocess
import pyautogui

from utils.logger import log_info, log_error


class WindowsController:

    def open_notepad(self):
        try:
            subprocess.Popen("notepad.exe")
            log_info("Notepad Opened")
        except Exception as e:
            log_error(str(e))

    def open_calculator(self):
        try:
            subprocess.Popen("calc.exe")
            log_info("Calculator Opened")
        except Exception as e:
            log_error(str(e))

    def open_cmd(self):
        try:
            subprocess.Popen("cmd.exe")
            log_info("CMD Opened")
        except Exception as e:
            log_error(str(e))

    def open_paint(self):
        try:
            subprocess.Popen("mspaint.exe")
            log_info("Paint Opened")
        except Exception as e:
            log_error(str(e))

    def open_explorer(self):
        try:
            subprocess.Popen("explorer.exe")
            log_info("File Explorer Opened")
        except Exception as e:
            log_error(str(e))

    def take_screenshot(self, filename="screenshot.png"):
        try:
            image = pyautogui.screenshot()
            image.save(filename)

            log_info(f"Screenshot Saved : {filename}")

        except Exception as e:
            log_error(str(e))

    def lock_pc(self):
        try:
            os.system("rundll32.exe user32.dll,LockWorkStation")

            log_info("PC Locked")

        except Exception as e:
            log_error(str(e))