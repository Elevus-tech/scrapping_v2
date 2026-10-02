from . import BaseSite


class YamahaSite(BaseSite):

    BASE_URL = "https://www.yamaha-motor.com.br/"

    def search(self, query):

        page = self.browser.new_page()

        try:

            print("   🌐 Abrindo Yamaha...")

            page.goto(
                self.BASE_URL,
                wait_until="domcontentloaded",
                timeout=60000
            )

            page.wait_for_timeout(3000)

            # ============================================================
            # 1. TENTAR FECHAR POPUPS / COOKIES
            # ============================================================

            self.fechar_popups(page)

            page.wait_for_timeout(1000)

            # ============================================================
            # 2. LOCALIZAR CAMPO DE BUSCA VISÍVEL
            # ============================================================

            search = page.locator(
                'input[placeholder*="Buscar"]'
            ).filter(
                visible=True
            ).first

            # Caso o seletor acima não encontre um campo visível,
            # tentamos outros campos de busca comuns.
            if not search.is_visible():

                print("   🔍 Campo de busca visível não encontrado.")

                candidatos = [
                    'input[type="search"]',
                    'input[aria-label*="Buscar"]',
                    'input[placeholder*="buscar"]',
                    'input[placeholder*="BUSCAR"]',
                    'input[placeholder*="Digite"]',
                ]

                search = None

                for seletor in candidatos:

                    try:

                        locator = page.locator(seletor).filter(
                            visible=True
                        ).first

                        if locator.is_visible():

                            search = locator

                            print(
                                f"   ✅ Campo encontrado: {seletor}"
                            )

                            break

                    except Exception:
                        continue

            if not search:

                raise Exception(
                    "Campo de busca visível da Yamaha não foi encontrado."
                )

            # ============================================================
            # 3. PREENCHER BUSCA
            # ============================================================

            print(
                f"   🔎 Pesquisando: {query}"
            )

            search.click()

            search.fill(query)

            page.wait_for_timeout(500)

            search.press("Enter")

            page.screenshot(
                path="debug/yamaha_busca.png",
                full_page=True
            )

            page.wait_for_timeout(5000)

            print("\n========== DEBUG LINKS RESULTADO ==========")

            links = page.locator('a[href*="/product/"]')

            for i in range(links.count()):

                link = links.nth(i)

                try:

                    texto = link.inner_text().strip()
                    href = link.get_attribute("href")

                    if texto and (
                        "FACTOR" in texto.upper()
                        or "MOVE BRASIL" in texto.upper()
                    ):

                        print("\n--- LINK ---")
                        print("TEXTO:", texto)
                        print("URL:", href)

                        print(
                            "HTML:",
                            link.evaluate(
                                "(el) => el.outerHTML"
                            )[:3000]
                        )

                except Exception:
                    continue

            print("========== FIM DEBUG LINKS ==========\n")

            # ============================================================
            # 4. AGUARDAR RESULTADOS
            # ============================================================

            page.wait_for_timeout(3000)

            products = []

            links = page.locator(
                'a[href*="/product/"][class*="bg-neutral-600"]'
            )

            total_links = links.count()

            print(
                f"   📦 Links de produtos encontrados: {total_links}"
            )

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

    # ================================================================
    # POPUPS
    # ================================================================

    def fechar_popups(self, page):

        seletores = [

            # Cookies / LGPD
            'button:has-text("Aceitar")',
            'button:has-text("Aceitar todos")',
            'button:has-text("Aceitar cookies")',
            'button:has-text("Concordo")',

            # Possíveis variações
            '[role="button"]:has-text("Aceitar")',
            '[role="button"]:has-text("Concordo")',

            # Fechar modal
            'button[aria-label="Fechar"]',
            'button[aria-label="Close"]',
            '[aria-label="Fechar"]',
            '[aria-label="Close"]',

        ]

        for seletor in seletores:

            try:

                elementos = page.locator(seletor)

                quantidade = elementos.count()

                for i in range(quantidade):

                    elemento = elementos.nth(i)

                    if elemento.is_visible():

                        try:

                            elemento.click(
                                timeout=2000
                            )

                            print(
                                f"   🍪 Popup fechado: {seletor}"
                            )

                            page.wait_for_timeout(500)

                            return

                        except Exception:
                            continue

            except Exception:
                continue

    # ================================================================
    # PRODUTO
    # ================================================================

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
                "price": self.extract_price(body),
                "description": body,
                "url": url
            }

        finally:

            page.close()

    @staticmethod
    def extract_price(text):

        import re

        matches = re.findall(
            r"R\$\s*[\d\.]+,\d{2}",
            text
        )

        if not matches:
            return None

        return matches[0]