"""
Script de integração para validar o pipeline completo da arquitetura dinâmica.
Fluxo: Busca -> Descoberta de Cards -> Match/Score -> Página do Produto -> Extração (Preço/HTML).
"""

import logging
from browser import Browser
from ai.agent import AIAgent
from engine.search import SearchEngine
from engine.product import ProductEngine
from matcher import ordenar_resultados

# Configuração formal para exibição de logs no terminal
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def run_integration_test():
    """
    Executa a simulação do fluxo principal de extração para um produto específico.
    """
    print("========================================")
    print(" 🚀 INICIANDO TESTE DE PIPELINE COMPLETO")
    print("========================================")

    url_alvo = "https://www.yamaha-motor.com.br/"
    termo_pesquisa = "DISCO FREIO DIANTEIRO FAZER 150" # Termo baseado no seu contexto
    
    browser_manager = Browser(headless=False)
    
    try:
        # Inicialização dos serviços
        browser_manager.start()
        page = browser_manager.new_page()
        
        agent = AIAgent()
        search_engine = SearchEngine(agent)
        product_engine = ProductEngine(agent)
        
        # ==========================================
        # ETAPA 1 e 2: Acessar e Buscar
        # ==========================================
        logger.info(f"Acessando o site base: {url_alvo}")
        page.goto(url_alvo, wait_until="networkidle", timeout=60000)
        
        sucesso_busca = search_engine.perform_search(page, termo_pesquisa)
        if not sucesso_busca:
            logger.error("Falha ao executar a pesquisa. Abortando pipeline.")
            return

        # ==========================================
        # ETAPA 3: Extrair Candidatos
        # ==========================================
        candidatos = search_engine.extract_candidates(page)
        if not candidatos:
            logger.error("Nenhum candidato encontrado na página de resultados.")
            return
            
        # ==========================================
        # ETAPA 4: Matcher (RapidFuzz)
        # ==========================================
        logger.info("Enviando candidatos para o algoritmo de similaridade (RapidFuzz)...")
        resultados_ranqueados = ordenar_resultados(termo_pesquisa, candidatos)
        
        if not resultados_ranqueados:
            logger.warning("Nenhum resultado sobreviveu ao filtro de similaridade.")
            return
            
        melhor_candidato = resultados_ranqueados[0]
        score = melhor_candidato["score"]
        
        logger.info(f"🏆 Melhor candidato: '{melhor_candidato['name']}'")
        logger.info(f"📊 Score de confiança: {score}")
        
        if score < 85:
            logger.warning("Score abaixo do limiar de segurança (85). Pipeline interrompido preventivamente.")
            return
            
        # ==========================================
        # ETAPA 5, 6 e 7: Produto (Preço e HTML)
        # ==========================================
        dados_produto = product_engine.extract_product_details(page, melhor_candidato["url"])
        
        if dados_produto:
            print("\n========================================")
            print(" ✅ DADOS EXTRAÍDOS COM SUCESSO")
            print("========================================")
            print(f"💰 PREÇO: {dados_produto.get('price')}")
            print("\n📝 DESCRIÇÃO HTML (Preview dos primeiros 500 caracteres):")
            
            html = dados_produto.get('description_html')
            if html:
                print(f"{html[:500]}...\n[CONTINUA...]")
            else:
                print("Nenhuma descrição capturada.")
            print("========================================\n")
            
    except Exception as exception:
        logger.error(f"Falha crítica no pipeline de integração: {str(exception)}")
        
    finally:
        logger.info("Encerrando recursos do navegador...")
        browser_manager.close()


if __name__ == "__main__":
    run_integration_test()