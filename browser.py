from playwright.sync_api import sync_playwright


class Browser:

    def __init__(self, headless=False):

        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None

    def start(self):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=self.headless
        )

        self.context = self.browser.new_context(
            viewport={
                "width": 1440,
                "height": 900
            },
            locale="pt-BR",
            user_agent=(
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/140.0.0.0 Safari/537.36"
            )
        )

    def new_page(self):

        return self.context.new_page()

    def close(self):

        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()