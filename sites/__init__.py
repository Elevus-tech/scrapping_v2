class BaseSite:

    def __init__(self, browser):

        self.browser = browser

    def search(self, query):
        raise NotImplementedError

    def get_product(self, url):
        raise NotImplementedError