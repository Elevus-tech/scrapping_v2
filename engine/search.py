"""
Módulo responsável por orquestrar a execução de buscas genéricas em lojas virtuais.
Realiza a integração entre a descoberta dinâmica de seletores (via IA) e a 
interação direta com o navegador (via Playwright).
"""

import logging
import time
from typing import Optional, Dict, Any
from playwright.sync_api import Page

from ai.agent import AIAgent

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class SearchEngine:
    """
    Mecanismo agnóstico de site para realizar buscas de produtos.
    """

    def __init__(self, agent: AIAgent):
        """
        Inicializa o mecanismo de busca.

        :param agent: Instância do AIAgent para processamento do DOM.
        """
        self.agent = agent

    def perform_search(self, page: Page, query: str) -> bool:
        """
        Localiza dinamicamente o campo de busca e executa a pesquisa.

        :param page: Instância da página atual do Playwright.
        :param query: Termo de busca (nome do produto).
        :return: True se a busca foi executada com sucesso, False caso contrário.
        """
        logger.info(f"Iniciando busca dinâmica para: '{query}'")

        # Aqui poderíamos injetar uma lógica de Cache antes de chamar a IA.
        # Por enquanto, chamamos a IA diretamente para descoberta.
        ai_response: Dict[str, Any] = self.agent.find_search_field(page)

        if not ai_response.get("success") or not ai_response.get("selector"):
            logger.error("A IA não conseguiu identificar o campo de busca.")
            logger.debug(f"Motivo reportado: {ai_response.get('reason')}")
            return False

        selector = ai_response["selector"]
        logger.info(f"Seletor identificado pela IA: {selector} (Confiança: {ai_response.get('confidence')})")

        return self._execute_search_action(page, selector, query)

    def _execute_search_action(self, page: Page, selector: str, query: str) -> bool:
        """
        Interage com o elemento do DOM para preencher a consulta e submetê-la.

        :param page: Instância da página atual do Playwright.
        :param selector: Seletor CSS do campo de busca.
        :param query: Termo de busca.
        :return: True se as ações no DOM ocorreram sem erros, False caso contrário.
        """
        try:
            target_locator = page.locator(selector).first
            
            # Aguarda o elemento estar visível para evitar interações prematuras
            target_locator.wait_for(state="visible", timeout=10000)

            logger.info("Preenchendo o campo de busca...")
            target_locator.click()
            target_locator.fill(query)
            
            # Pausa breve para emular comportamento humano (debounce do site)
            time.sleep(0.5)

            logger.info("Submetendo pesquisa (pressionando Enter)...")
            target_locator.press("Enter")

            # Aguarda o carregamento inicial da página de resultados
            page.wait_for_load_state("domcontentloaded")
            
            return True

        except Exception as error:
            logger.error(f"Falha ao executar ação de busca com o seletor '{selector}': {error}")
            return False