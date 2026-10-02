"""
Script de teste isolado para a Etapa 2B da arquitetura dinâmica.
Objetivo: Validar a descoberta dinâmica dos cards de produtos na página de resultados.
"""

import time
import logging
from browser import Browser
from ai.agent import AIAgent

# Desativando logs de debug excessivos para limpar o terminal
logging.getLogger("httpx").setLevel(logging.WARNING)


def run_test():
    """
    Executa o fluxo de teste: navegação, busca automatizada e análise da página de resultados.
    """
    print("========================================")
    print("  AGENTE IA — DESCOBERTA DE RESULTADOS  ")
    print("========================================")

    url_alvo = "https://www.yamaha-motor.com.br/"
    browser_manager = Browser(headless=False)
    
    try:
        browser_manager.start()
        page = browser_manager.new_page()
        agent = AIAgent()
        
        print(f"\n[1] Navegando para o site: {url_alvo}")
        page.goto(url_alvo, wait_until="networkidle", timeout=60000)
        
        print("[2] Localizando o campo de busca dinamicamente...")
        busca_info = agent.find_search_field(page)
        seletor_busca = busca_info.get("selector")
        
        if not seletor_busca:
            print("\n[ERRO] Falha ao encontrar campo de busca. Abortando o teste.")
            return

        print("[3] Contornando overlays e realizando pesquisa de teste...")
        campo = page.locator(seletor_busca).first
        
        # Aguarda a presença do elemento no DOM, ignorando se está coberto por overlays
        campo.wait_for(state="attached", timeout=10000)
        
        # A flag force=True ignora elementos sobrepostos (como modais de cookies)
        # e despacha os eventos de clique e teclado diretamente no elemento alvo.
        campo.click(force=True)
        campo.fill("FACTOR", force=True)
        
        time.sleep(1)  # Breve pausa para emular comportamento humano e acionar listeners
        
        # Dispara o evento de submissão do formulário
        campo.press("Enter")
        
        print("[4] Aguardando o carregamento da página de resultados...")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(4)  # Aguarda a renderização de componentes dinâmicos (React/Vue)
        
        print("[5] Iniciando o Agente IA para análise do DOM de resultados...")
        resultado = agent.identify_search_results(page)
        
        print("\n--- RESULTADO DA IA (CARDS) ---")
        print(f"Sucesso:           {resultado.get('success')}")
        print(f"Seletor do Card:   {resultado.get('card_selector')}")
        print(f"Seletor do Nome:   {resultado.get('name_selector')}")
        print(f"Seletor do Link:   {resultado.get('link_selector')}")
        print(f"Confiança:         {resultado.get('confidence')}")
        print(f"Motivo:            {resultado.get('reason')}")
        
        print("\n[6] Validando os seletores no ambiente do Playwright...")
        card_selector = resultado.get('card_selector')
        
        if card_selector:
            cards = page.locator(card_selector)
            quantidade = cards.count()
            print(f"Quantidade de cards encontrados no DOM: {quantidade}")
            
            if quantidade > 0:
                print("Selector válido: SIM (Destacando os 3 primeiros resultados com borda verde)")
                
                # Aplica estilo visual aos primeiros elementos localizados para confirmação
                for i in range(min(quantidade, 3)):
                    cards.nth(i).evaluate("el => el.style.border = '4px solid green'")
                
                # Aguarda para visualização do usuário
                page.wait_for_timeout(5000)
            else:
                print("Selector válido: NÃO (Nenhum elemento corresponde ao seletor gerado)")
        else:
            print("Selector válido: NÃO (O provedor de IA não retornou um seletor válido)")

    except Exception as exception:
        print(f"\n[ERRO FATAL] Ocorreu uma falha na execução do teste: {str(exception)}")
        
    finally:
        print("\n[7] Fechando recursos de navegação...")
        browser_manager.close()
        print("========================================")


if __name__ == "__main__":
    run_test()