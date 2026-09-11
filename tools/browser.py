"""
PARTH AI - Browser Engine V5
"""

from urllib.parse import urlparse, parse_qs, quote_plus

from playwright.sync_api import sync_playwright

from utils.logger import log_info, log_error


class BrowserActionError(RuntimeError):
    """A safe error message that the Agent can speak."""


class Browser:

    def __init__(self):

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self._youtube_page = None
        self._owns_browser = False
        self._video_history = {}

    # --------------------------------------
    # Start Browser
    # --------------------------------------

    def start(self):
        if self.browser is not None and self.browser.is_connected():
            return
        try:
            if self.playwright is None:
                self.playwright = sync_playwright().start()
            try:
                self.browser = self.playwright.chromium.connect_over_cdp(
                    "http://127.0.0.1:9222", timeout=3000
                )
                self._owns_browser = False
                self.context = (self.browser.contexts[0] if self.browser.contexts
                                else self.browser.new_context())
                log_info("Connected to Chrome")
            except Exception:
                self.browser = self.playwright.chromium.launch(channel="chrome", headless=False)
                self._owns_browser = True
                self.context = self.browser.new_context()
                log_info("Launched new Chrome")
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        except Exception as e:
            log_error(f"Browser Start Error : {e}")
            self.close()
            raise BrowserActionError("Sorry sir, I couldn't open Chrome.") from e

    # --------------------------------------
    # Open URL
    # --------------------------------------

    def open_url(self, url):
        try:
            if not isinstance(url, str) or not url.strip():
                raise BrowserActionError("Please provide a website address.")
            url = url.strip()
            if "://" not in url:
                url = "https://" + url
            parsed = urlparse(url)
            if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
                raise BrowserActionError("Please provide an HTTP or HTTPS website address.")
            self._ensure_page()
            self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            log_info(f"Opened {url}")
            return True
        except BrowserActionError:
            raise
        except Exception as e:
            log_error(f"Open URL Error : {e}")
            raise BrowserActionError("Sorry sir, I couldn't open that page.") from e

    # --------------------------------------
    # Google Search
    # --------------------------------------

    def google_search(self, query):
        if not isinstance(query, str) or not query.strip():
            raise BrowserActionError("What would you like me to search for?")
        return self.open_url("https://www.google.com/search?q=" + quote_plus(query.strip()))

    # --------------------------------------
    # YouTube Search + Play
    # --------------------------------------

    def youtube_search(self, query):
        try:
            if not isinstance(query, str) or not query.strip():
                raise BrowserActionError("Which song would you like me to play?")
            self._ensure_page()
            # Reuse PARTH's YouTube tab when it still exists.
            if self._is_youtube(self._youtube_page):
                self.page = self._youtube_page
            self._remember_video(self.page)
            log_info(f"YouTube Search : {query}")
            self.open_url("https://www.youtube.com/results?search_query=" + quote_plus(query.strip()))
            self._youtube_page = self.page
            video = self.page.locator("ytd-video-renderer a#video-title").first
            video.wait_for(state="visible", timeout=15000)
            video.click(timeout=10000)
            self.page.wait_for_function(
                "() => !!new URL(location.href).searchParams.get('v')",
                timeout=15000,
            )
            self.play_video()
            self._remember_video(self.page)
            log_info(f"Playing YouTube : {query}")
            return True
        except BrowserActionError:
            raise
        except Exception as e:
            log_error(f"YouTube Error : {e}")
            raise BrowserActionError(
                "Sorry sir, I couldn't start that video. Please check YouTube for a consent or sign-in screen."
            ) from e

    # ======================================
    # YouTube Controls
    # ======================================

    # --------------------------------------
    # Play / Resume
    # --------------------------------------

    def play_video(self):
        return self._video_action("play_video")

    # --------------------------------------
    # Pause
    # --------------------------------------

    def pause_video(self):
        return self._video_action("pause_video")

    # --------------------------------------
    # Stop
    # --------------------------------------

    def stop_video(self):
        return self._video_action("stop_video")

    # --------------------------------------
    # Next Video
    # --------------------------------------

    def next_video(self):
        return self._change_video(previous=False)

    # --------------------------------------
    # Previous Video
    # --------------------------------------

    def previous_video(self):
        return self._change_video(previous=True)

    # --------------------------------------
    # Volume Up
    # --------------------------------------

    def volume_up(self):
        return self._video_action("volume_up")

    # --------------------------------------
    # Volume Down
    # --------------------------------------

    def volume_down(self):
        return self._video_action("volume_down")

    # --------------------------------------
    # Mute
    # --------------------------------------

    def mute(self):
        return self._video_action("mute")

    # --------------------------------------
    # Unmute
    # --------------------------------------

    def unmute(self):
        return self._video_action("unmute")

    # --------------------------------------
    # Click
    # --------------------------------------

    def click(self, selector):

        self.page.locator(
            selector
        ).click()

    # --------------------------------------
    # Type
    # --------------------------------------

    def type(self, selector, text):

        self.page.locator(
            selector
        ).fill(text)

    # --------------------------------------
    # Scroll Down
    # --------------------------------------

    def scroll_down(self, pixels=1200):

        self.page.mouse.wheel(
            0,
            pixels
        )

    # --------------------------------------
    # Scroll Up
    # --------------------------------------

    def scroll_up(self, pixels=1200):

        self.page.mouse.wheel(
            0,
            -pixels
        )

    # --------------------------------------
    # Back
    # --------------------------------------

    def back(self):

        self.page.go_back()

    # --------------------------------------
    # Forward
    # --------------------------------------

    def forward(self):

        self.page.go_forward()

    # --------------------------------------
    # Refresh
    # --------------------------------------

    def refresh(self):

        self.page.reload()

    # --------------------------------------
    # New Tab
    # --------------------------------------

    def new_tab(self, url="about:blank"):

        page = self.context.new_page()

        page.goto(url)

        self.page = page

    # --------------------------------------
    # Switch Tab
    # --------------------------------------

    def switch_tab(self, index):

        self.page = (
            self.context.pages[index]
        )

    # --------------------------------------
    # Read Page
    # --------------------------------------

    def read_page(self):

        return self.page.locator(
            "body"
        ).inner_text()

    # --------------------------------------
    # Close
    # --------------------------------------

    def close(self):
        try:
            # Only close a Chrome process that PARTH launched itself.
            if self.browser and self._owns_browser:
                self.browser.close()
        except Exception as e:
            log_error(f"Browser Close Error : {e}")
        finally:
            try:
                if self.playwright:
                    self.playwright.stop()
            except Exception as e:
                log_error(f"Playwright Close Error : {e}")
            self.playwright = None
            self.browser = None
            self.context = None
            self.page = None
            self._youtube_page = None
            self._owns_browser = False
            self._video_history.clear()

    def _ensure_page(self):
        if self.browser is None or not self.browser.is_connected():
            self.start()
        if self.page is None or self.page.is_closed():
            self.page = self.context.new_page()

    @staticmethod
    def _is_youtube(page):
        if page is None or page.is_closed():
            return False
        host = (urlparse(page.url).hostname or "").lower()
        return host == "youtube.com" or host.endswith(".youtube.com")

    @staticmethod
    def _video_id(url):
        return parse_qs(urlparse(url).query).get("v", [""])[0]

    def _get_youtube_page(self):
        # Current YouTube page first, then the remembered tab. Never silently
        # select an arbitrary one when several other YouTube tabs are open.
        if self._is_youtube(self.page):
            page = self.page
        elif self._is_youtube(self._youtube_page):
            page = self._youtube_page
        else:
            pages = [] if self.context is None else [
                p for p in self.context.pages if self._is_youtube(p)
            ]
            if len(pages) > 1:
                raise BrowserActionError("Several YouTube tabs are open. Ask me to play a song first.")
            if not pages:
                raise BrowserActionError("No YouTube video is open. Ask me to play a song first.")
            page = pages[0]
        self._youtube_page = page
        page.bring_to_front()
        try:
            page.locator("video").first.wait_for(state="attached", timeout=10000)
        except Exception as e:
            raise BrowserActionError("I couldn't find a video on that YouTube page.") from e
        self._remember_video(page)
        return page

    def _remember_video(self, page):
        if not self._is_youtube(page) or not self._video_id(page.url):
            return
        history = self._video_history.setdefault(page, [])
        if not history or self._video_id(history[-1]) != self._video_id(page.url):
            history.append(page.url)
            del history[:-50]

    def _video_action(self, action):
        try:
            page = self._get_youtube_page()
            status = page.evaluate("""
                async (action) => {
                    const video = document.querySelector('video');
                    if (!video) return {ok: false, reason: 'missing'};
                    if (action === 'play_video') {
                        let timer;
                        try {
                            await Promise.race([
                                video.play(),
                                new Promise((_, reject) => {
                                    timer = setTimeout(() => reject(new Error('Playback timeout')), 8000);
                                })
                            ]);
                        } finally {
                            clearTimeout(timer);
                        }
                        if (video.paused) return {ok: false, reason: 'paused'};
                    } else if (action === 'pause_video') {
                        video.pause();
                    } else if (action === 'stop_video') {
                        video.pause();
                        video.currentTime = 0;
                    } else if (action === 'volume_up') {
                        if (video.volume >= 1 && !video.muted)
                            return {ok: false, reason: 'maximum'};
                        video.volume = Math.min(1, video.volume + 0.1);
                        video.muted = false;
                    } else if (action === 'volume_down') {
                        if (video.volume <= 0) return {ok: false, reason: 'minimum'};
                        video.volume = Math.max(0, video.volume - 0.1);
                    } else if (action === 'mute') {
                        video.muted = true;
                    } else if (action === 'unmute') {
                        video.muted = false;
                    } else {
                        return {ok: false, reason: 'unsupported'};
                    }
                    return {ok: true};
                }
            """, action)
            if not isinstance(status, dict) or status.get("ok") is not True:
                reason = status.get("reason") if isinstance(status, dict) else ""
                if reason == "maximum":
                    raise BrowserActionError("The video volume is already at maximum.")
                if reason == "minimum":
                    raise BrowserActionError("The video volume is already at minimum.")
                raise BrowserActionError("Sorry sir, the video control did not complete.")
            log_info(f"YouTube control completed : {action}")
            return True
        except BrowserActionError:
            raise
        except Exception as e:
            log_error(f"YouTube Control Error ({action}) : {e}")
            raise BrowserActionError("Sorry sir, I couldn't control that video.") from e

    def _change_video(self, previous=False):
        try:
            page = self._get_youtube_page()
            old_id = self._video_id(page.url)
            if not old_id:
                raise BrowserActionError("Please open a YouTube watch page first.")
            in_playlist = bool(parse_qs(urlparse(page.url).query).get("list"))
            history = self._video_history.setdefault(page, [])
            if previous and not in_playlist:
                if len(history) < 2:
                    raise BrowserActionError("There is no previous video in this session. Try a playlist first.")
                target = history[-2]
                page.goto(target, wait_until="domcontentloaded", timeout=30000)
                # Update history only after navigation succeeded.
                history.pop()
            else:
                # Focus the player without a click that could toggle playback.
                # This also avoids typing the shortcut into the search field.
                page.locator("video").first.evaluate("v => { v.tabIndex = 0; v.focus(); }")
                page.keyboard.press("Shift+P" if previous else "Shift+N")
            page.wait_for_function(
                "oldId => { const id = new URL(location.href).searchParams.get('v'); return !!id && id !== oldId; }",
                arg=old_id, timeout=12000,
            )
            # The controlled tab may differ from the general browser page.
            saved_page = self.page
            self.page = page
            try:
                self.play_video()
            finally:
                self.page = saved_page
            self._remember_video(page)
            return True
        except BrowserActionError:
            raise
        except Exception as e:
            log_error(f"YouTube Navigation Error : {e}")
            direction = "previous" if previous else "next"
            raise BrowserActionError(f"Sorry sir, I couldn't start the {direction} video.") from e
