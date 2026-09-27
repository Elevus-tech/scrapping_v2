from . import BaseSite

from utils import extract_price


class YamahaSite(BaseSite):

    BASE_URL = "https://www.yamaha-motor.com.br/"

    def search(self, query):

        page = self.browser.new_page()

        try:

            page.goto(
                self.BASE_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            search = page.locator(
                'input[placeholder*="Buscar"]'
            ).first

            search.fill(query)

            page.wait_for_timeout(2000)

            products = []

            links = page.locator(
                'a[href*="/product/"]'
            )

            total_links = links.count()

            for i in range(total_links):

                link = links.nth(i)

                try:

                    name = link.inner_text().strip()

                    url = link.get_attribute(
                        "href"
                    )

                    if name and url:

                        if url.startswith("/"):

                            url = (
                                self.BASE_URL.rstrip("/")
                                + url
                            )

                        products.append({
                            "name": name,
                            "url": url
                        })

                except Exception:

                    continue

            return products

        finally:

            page.close()

    def get_product(self, url):

        page = self.browser.new_page()

        try:

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            page.wait_for_timeout(1000)

            title = page.locator(
                "h1"
            ).first.inner_text()

            body = page.locator(
                "body"
            ).inner_text()

            return {
                "name": title.strip(),
                "price": extract_price(body),
                "description": body,
                "url": url
            }

        finally:

            page.close()