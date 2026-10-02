"""
Módulo responsável por orquestrar a execução de buscas genéricas em lojas virtuais.
Realiza a integração entre a descoberta dinâmica de seletores (via IA) e a
interação direta com o navegador (via Playwright).
"""

import logging
import time
from typing import Dict, Any, List
from playwright.sync_api import Page

from ai.agent import AIAgent

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class SearchEngine:
    """
    Mecanismo agnóstico de site para realizar buscas de produtos e extrair candidatos.
    """

    def __init__(self, agent: AIAgent):
        """
        Inicializa o mecanismo de busca genérico.

        :param agent: Instância do AIAgent para processamento do DOM.
        """
        self.agent = agent

    def perform_search(self, page: Page, query: str) -> bool:
        """
        Localiza dinamicamente o campo de busca, contorna overlays e executa a pesquisa.

        :param page: Instância da página atual do Playwright.
        :param query: Termo de busca (nome do produto).
        :return: True se a busca foi executada com sucesso, False caso contrário.
        """
        logger.info(f"Iniciando busca dinâmica para o termo: '{query}'")

        ai_response: Dict[str, Any] = self.agent.find_search_field(page)

        if not ai_response.get("success") or not ai_response.get("selector"):
            logger.error("A IA não conseguiu identificar o campo de busca.")
            return False

        selector = ai_response["selector"]
        logger.info(f"Seletor de busca mapeado: {selector}")

        return self._execute_search_action(page, selector, query)

    def _execute_search_action(self, page: Page, selector: str, query: str) -> bool:
        """
        Injeta a pesquisa diretamente no DOM, contornando modais intrusivos.
        """
        try:
            target_locator = page.locator(selector).first
            target_locator.wait_for(state="attached", timeout=10000)

            logger.info("Injetando termo de pesquisa e submetendo formulário...")
            target_locator.click(force=True)
            target_locator.fill(query, force=True)
            
            time.sleep(1)
            target_locator.press("Enter")
            
            # Aguarda a navegação e a renderização dos componentes reativos
            page.wait_for_load_state("domcontentloaded")
            time.sleep(3)
            
            return True

        except Exception as error:
            logger.error(f"Falha na execução da ação de busca: {error}")
            return False

    def extract_candidates(self, page: Page) -> List[Dict[str, str]]:
        """
        Aciona a IA para mapear a estrutura dos resultados e extrai os dados dos cards.

        :param page: Instância da página atual contendo os resultados.
        :return: Lista de dicionários contendo o 'name' e a 'url' de cada produto.
        """
        logger.info("Solicitando à IA o mapeamento da estrutura dos cards de resultado...")
        ai_response = self.agent.identify_search_results(page)

        if not ai_response.get("success") or not ai_response.get("card_selector"):
            logger.error("A IA não foi capaz de identificar o padrão estrutural dos cards.")
            return []

        card_selector = ai_response["card_selector"]
        name_selector = ai_response.get("name_selector", "")
        link_selector = ai_response.get("link_selector", "")
        
        logger.info(f"Padrão de card identificado: '{card_selector}'")
        
        return self._parse_cards(page, card_selector, name_selector, link_selector)

    def _parse_cards(self, page: Page, card_selector: str, name_selector: str, link_selector: str) -> List[Dict[str, str]]:
        """
        Itera sobre os nós do DOM e normaliza os dados de nome e URL dos candidatos.
        """
        candidates = []
        try:
            cards = page.locator(card_selector)
            count = cards.count()
            
            logger.info(f"Iniciando raspagem de {count} elementos correspondentes...")

            for i in range(count):
                card = cards.nth(i)
                
                try:
                    # Resolve o nome com fallback para o innerText do próprio card principal
                    if not name_selector:
                        name = card.inner_text().strip()
                    else:
                        name = card.locator(name_selector).first.inner_text().strip()

                    # Resolve o link com fallback para o href do próprio card principal
                    if not link_selector:
                        url = card.get_attribute("href")
                    else:
                        url = card.locator(link_selector).first.get_attribute("href")

                    if name and url:
                        # Normalização preventiva para URLs relativas
                        if url.startswith("/"):
                            base_url = "/".join(page.url.split("/")[:3])
                            url = base_url + url

                        candidates.append({
                            "name": name,
                            "url": url
                        })
                except Exception:
                    continue
                    
            logger.info(f"Extração concluída: {len(candidates)} candidatos válidos processados.")
            return candidates

        except Exception as error:
            logger.error(f"Ocorreu um erro no loop de parsing do DOM: {error}")
            return candidates