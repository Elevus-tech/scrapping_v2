"""
Módulo responsável por acessar a página individual do produto,
identificar dinamicamente os elementos de preço e descrição via IA,
e extrair os dados formatados (incluindo preservação do HTML).
"""

import logging
from typing import Dict, Any, Optional
from playwright.sync_api import Page

from ai.agent import AIAgent
from utils import extract_price

# Configuração formal para exibição de logs no terminal
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class ProductEngine:
    """
    Mecanismo para processamento e extração dinâmica de dados na página de detalhes do produto.
    """

    def __init__(self, agent: AIAgent):
        """
        Inicializa o mecanismo de extração de produto.

        :param agent: Instância do AIAgent para processamento do DOM.
        """
        self.agent = agent

    def extract_product_details(self, page: Page, url: str) -> Optional[Dict[str, Any]]:
        """
        Navega até a URL do produto, aciona a IA para mapeamento do DOM e extrai
        o preço e a descrição, preservando a estrutura HTML original.

        :param page: Instância da página atual do Playwright.
        :param url: Link direto para o produto mapeado pelo SearchEngine.
        :return: Dicionário contendo os dados extraídos ou None em caso de falha.
        """
        logger.info(f"Iniciando navegação para a página do produto: {url}")
        
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Aguarda tempo hábil para execução de scripts de precificação dinâmica
            page.wait_for_timeout(2500)  
            
            logger.info("Solicitando à IA o mapeamento dos elementos estruturais do produto...")
            ai_response = self.agent.identify_product_data(page)
            
            if not ai_response.get("success"):
                logger.error("O provedor de IA não conseguiu determinar a estrutura da página.")
                return None
                
            price_selector = ai_response.get("price_selector")
            desc_selector = ai_response.get("description_selector")
            
            logger.info(f"Seletores mapeados - Preço: '{price_selector}' | Descrição: '{desc_selector}'")
            
            # ==========================================
            # Extração de Preço
            # ==========================================
            preco_final = None
            if price_selector:
                price_element = page.locator(price_selector).first
                if price_element.is_visible():
                    texto_preco = price_element.inner_text()
                    preco_final = extract_price(texto_preco)
                    logger.info(f"Preço bruto extraído e formatado: {preco_final}")
            
            # ==========================================
            # Extração de Descrição (HTML preservado)
            # ==========================================
            descricao_html = None
            if desc_selector:
                desc_element = page.locator(desc_selector).first
                if desc_element.is_visible():
                    descricao_html = desc_element.inner_html()
                    tamanho = len(descricao_html) if descricao_html else 0
                    logger.info(f"Bloco de descrição extraído com sucesso ({tamanho} caracteres).")
            
            return {
                "url": url,
                "price": preco_final,
                "description_html": descricao_html
            }

        except Exception as error:
            logger.error(f"Falha sistêmica durante a extração de dados do produto: {error}")
            return None