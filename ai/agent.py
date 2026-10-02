import json
import os
import logging

from openai import OpenAI

from .dom_analyzer import DOMAnalyzer
from .prompts import (
    SEARCH_FIELD_PROMPT,
    RESULTS_PROMPT,
    PRODUCT_PROMPT,
)

# Configuração formal para exibição de logs no terminal
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class AIAgent:
    """
    Agente responsável por interpretar o DOM da página utilizando modelos de linguagem,
    retornando seletores de forma dinâmica e estruturada.
    """

    def __init__(self, api_key=None, model=None):
        # Agora buscando a variável de ambiente correta definida no PowerShell
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise RuntimeError("A variável de ambiente OPENAI_API_KEY não foi configurada adequadamente.")

        self.model = model or os.getenv("AI_MODEL", "gpt-4o-mini")
        
        # Inicialização do cliente oficial da OpenAI
        self.client = OpenAI(api_key=self.api_key)
        self.dom_analyzer = DOMAnalyzer()

    def find_search_field(self, page):
        """
        Analisa a página atual e solicita à IA a identificação do campo de busca.
        """
        logger.info("Iniciando a extração do DOM para identificação do campo de busca...")
        dom_data = self.dom_analyzer.analyze(page)
        
        # Converte o dicionário em uma string JSON para envio seguro ao modelo
        dom_json = json.dumps(dom_data, ensure_ascii=False)
        
        logger.info("Solicitando análise estruturada ao provedor de IA...")
        response = self._ask_ai(SEARCH_FIELD_PROMPT, dom_json)
        
        return self._parse_response(response)

    def identify_search_results(self, page):
        dom_data = self.dom_analyzer.analyze(page)
        response = self._ask_ai(RESULTS_PROMPT, json.dumps(dom_data, ensure_ascii=False))
        return self._parse_response(response)

    def identify_product_data(self, page):
        dom_data = self.dom_analyzer.analyze(page)
        response = self._ask_ai(PRODUCT_PROMPT, json.dumps(dom_data, ensure_ascii=False))
        return self._parse_response(response)

    def _ask_ai(self, system_prompt, user_data):
        """
        Executa a requisição formal à API da OpenAI, garantindo o retorno no formato JSON.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_data}
                ],
                temperature=0.1
            )
            return response.choices[0].message.content
            
        except Exception as exception:
            logger.error(f"Ocorreu um erro na comunicação com a API de IA: {str(exception)}")
            return json.dumps({
                "success": False,
                "selector": None,
                "confidence": 0,
                "reason": f"Erro interno da API: {str(exception)}"
            })

    def _parse_response(self, response):
        """
        Garante que a resposta obtida seja convertida corretamente para um dicionário Python.
        """
        if isinstance(response, dict):
            return response

        try:
            return json.loads(response)
        except json.JSONDecodeError as error:
            logger.error(f"Falha ao decodificar a resposta JSON: {error}")
            return {
                "success": False,
                "selector": None,
                "confidence": 0,
                "reason": f"O formato de resposta da IA é inválido: {error}"
            }