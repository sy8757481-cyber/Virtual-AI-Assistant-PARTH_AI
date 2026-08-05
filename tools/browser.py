
"""
PARTH AI - Browser Engine V3
"""
from playwright.sync_api import sync_playwright
from utils.logger import log_info, log_error

class Browser:
    def __init__(self):
        self.playwright=None
        self.browser=None
        self.context=None
        self.page=None

    def start(self):
        try:
            self.playwright=sync_playwright().start()
            self.browser=self.playwright.chromium.connect_over_cdp("http://127.0.0.1:9222")
            self.context=self.browser.contexts[0] if self.browser.contexts else self.browser.new_context()
            self.page=self.context.pages[0] if self.context.pages else self.context.new_page()
            log_info("Connected to Chrome")
        except Exception:
            self.browser=self.playwright.chromium.launch(channel="chrome",headless=False)
            self.context=self.browser.new_context()
            self.page=self.context.new_page()
            log_info("Launched new Chrome")

    def open_url(self,url):
        try:
            self.page.goto(url,wait_until="domcontentloaded")
            log_info(f"Opened {url}")
        except Exception as e:
            log_error(str(e))

    def google_search(self,query):
        self.open_url(f"https://www.google.com/search?q={query.replace(' ','+')}")

    def youtube_search(self,query):
        self.open_url("https://www.youtube.com")
        self.page.wait_for_selector("input[name='search_query']",timeout=10000)
        box=self.page.locator("input[name='search_query']")
        box.fill(query)
        box.press("Enter")

    def click(self,selector):
        self.page.locator(selector).click()

    def type(self,selector,text):
        self.page.locator(selector).fill(text)

    def scroll_down(self,pixels=1200):
        self.page.mouse.wheel(0,pixels)

    def scroll_up(self,pixels=1200):
        self.page.mouse.wheel(0,-pixels)

    def back(self):
        self.page.go_back()

    def forward(self):
        self.page.go_forward()

    def refresh(self):
        self.page.reload()

    def new_tab(self,url="about:blank"):
        p=self.context.new_page()
        p.goto(url)
        self.page=p

    def switch_tab(self,index):
        self.page=self.context.pages[index]

    def read_page(self):
        return self.page.locator("body").inner_text()

    def close(self):
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            log_error(str(e))