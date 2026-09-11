import subprocess
import time
import os


class ChromeLauncher:

    def __init__(self):

        self.chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

        self.user_data = os.path.join(
            os.getcwd(),
            "data",
            "chrome_profile"
        )

    def start(self):

        if not os.path.exists(self.user_data):
            os.makedirs(self.user_data)

        subprocess.Popen([
            self.chrome_path,
            "--remote-debugging-port=9222",
            f"--user-data-dir={self.user_data}"
        ])

        time.sleep(3)