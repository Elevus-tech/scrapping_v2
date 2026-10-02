"""
Módulo responsável por varrer o DOM e extrair elementos interativos 
para estruturação em JSON, servindo como base para análise da IA.
"""

from playwright.sync_api import Page


class DOMAnalyzer:

    def __init__(self, max_elements=250):
        self.max_elements = max_elements

    def analyze(self, page: Page):
        """
        Analisa a página atual e retorna uma representação simplificada 
        dos elementos relevantes. Adicionado suporte ampliado para tags estruturais.
        """
        # Incluímos article, li e divs com classes suspeitas de serem produtos
        elements = page.locator(
            "input, textarea, button, a, select, "
            "[role='button'], [role='search'], "
            "article, li, [class*='product'], [class*='card'], [class*='item']"
        )

        count = min(elements.count(), self.max_elements)
        results = []

        for i in range(count):
            try:
                element = elements.nth(i)

                if not element.is_visible():
                    continue

                tag = element.evaluate("(el) => el.tagName.toLowerCase()")
                text = self._safe_text(element)
                
                # Elementos vazios (sem texto e sem atributos úteis) são ruído
                if not text and tag not in ["input", "textarea"]:
                    continue

                placeholder = self._safe_attribute(element, "placeholder")
                aria_label = self._safe_attribute(element, "aria-label")
                href = self._safe_attribute(element, "href")
                input_type = self._safe_attribute(element, "type")
                css_class = self._safe_attribute(element, "class")
                selector = self._build_selector(element)

                item = {
                    "index": i,
                    "tag": tag,
                    "class": self._limit(css_class, 150),
                    "text": self._limit(text, 300),
                    "placeholder": self._limit(placeholder, 150),
                    "aria_label": self._limit(aria_label, 150),
                    "type": input_type,
                    "href": self._limit(href, 300),
                    "selector": selector,
                }

                results.append(item)

            except Exception:
                continue

        return {
            "url": page.url,
            "title": page.title(),
            "elements": results
        }

    def _safe_text(self, element):
        try:
            return element.inner_text().strip()
        except Exception:
            return ""

    def _safe_attribute(self, element, name):
        try:
            value = element.get_attribute(name)
            return value.strip() if value else ""
        except Exception:
            return ""

    def _limit(self, value, size):
        if not value:
            return ""
        value = str(value)
        return value if len(value) <= size else value[:size] + "..."

    def _build_selector(self, element):
        """
        Cria um seletor CSS inicializado via JavaScript.
        Agora suporta fragmentos de href e classes primárias.
        """
        try:
            return element.evaluate(
                """
                (el) => {
                    if (el.id) return "#" + CSS.escape(el.id);
                    
                    let base = el.tagName.toLowerCase();
                    
                    if (base === 'a' && el.getAttribute("href")) {
                        let href = el.getAttribute("href");
                        if (href.includes("/product/")) return 'a[href*="/product/"]';
                        if (href.includes("/p/")) return 'a[href*="/p/"]';
                    }
                    
                    if (el.className && typeof el.className === 'string') {
                        let classes = el.className.trim().split(/\s+/)
                            .filter(c => c.length > 2 && !c.includes(':') && !c.includes('['));
                        if (classes.length > 0) {
                            return base + "." + CSS.escape(classes[0]);
                        }
                    }
                    
                    if (el.getAttribute("name")) return base + '[name="' + CSS.escape(el.getAttribute("name")) + '"]';
                    if (el.getAttribute("placeholder")) return base + '[placeholder="' + CSS.escape(el.getAttribute("placeholder")) + '"]';
                    
                    return base;
                }
                """
            )
        except Exception:
            return ""