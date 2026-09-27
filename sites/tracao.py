from . import BaseSite

from utils import extract_price


class TracaoSite(BaseSite):

    BASE_URL = "https://www.tracaomotosyamaha.com.br/"

    def search(self, query):

        page = self.browser.new_page()

        try:

            page.goto(
                self.BASE_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            search = page.locator(
                'input[placeholder*="procura"]'
            ).first

            search.fill(query)

            search.press("Enter")

            page.wait_for_load_state(
                "domcontentloaded"
            )

            page.wait_for_timeout(1500)

            products = []

            links = page.locator("a")

            total_links = links.count()

            for i in range(
                min(total_links, 300)
            ):

                link = links.nth(i)

                try:

                    text = link.inner_text().strip()

                    href = link.get_attribute(
                        "href"
                    )

                    if (
                        href
                        and text
                        and len(text) > 5
                        and "R$" in text
                    ):

                        products.append({
                            "name": text,
                            "url": href
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