import os

from scraper import Browser

from excel import (
    carregar_produtos,
    salvar_preco
)

from matcher import ordenar_resultados

from sites.tracao import TracaoSite
from sites.yamaha import YamahaSite


INPUT_FILE = "input/planilha_produtos_formatada_v4.xlsx"

OUTPUT_FILE = "output/planilha_precos_atualizada.xlsx"


def main():

    print()
    print("=" * 80)
    print("🚀 SCRAPER DE PREÇOS")
    print("=" * 80)
    print()

    # ---------------------------------------------------------
    # 1. CARREGAR PLANILHA
    # ---------------------------------------------------------

    print("📊 Carregando planilha...")

    wb, ws, produtos = carregar_produtos(
        INPUT_FILE
    )

    print(
        f"Produtos carregados: {len(produtos)}"
    )

    # ---------------------------------------------------------
    # 2. INICIAR BROWSER
    # ---------------------------------------------------------

    browser = Browser(
        headless=False
    )

    browser.start()

    # ---------------------------------------------------------
    # 3. SITES ATIVOS
    # ---------------------------------------------------------

    sites = {

        "tracao": TracaoSite(
            browser
        ),

        "yamaha": YamahaSite(
            browser
        ),

        # Entram depois:
        #
        # "matsuo": MatsuoSite(browser),
        # "honda": HondaSite(browser),
        # "neno": NenoSite(browser),
    }

    try:

        # -----------------------------------------------------
        # 4. PROCESSAR PRODUTOS
        # -----------------------------------------------------

        for index, produto in enumerate(
            produtos,
            start=1
        ):

            row = produto["row"]

            nome = produto["nome"]

            sku = produto["sku"]

            woo_id = produto["id"]

            print()
            print("=" * 80)

            print(
                f"Produto {index}/{len(produtos)}"
            )

            print(
                f"ID: {woo_id}"
            )

            print(
                f"SKU: {sku}"
            )

            print(
                f"Nome: {nome}"
            )

            print("=" * 80)

            preco_encontrado = None

            # -------------------------------------------------
            # 5. BUSCAR EM CADA SITE
            # -------------------------------------------------

            for site_name, site in sites.items():

                print()
                print(
                    f"🔎 Buscando no {site_name}..."
                )

                try:

                    candidates = site.search(
                        nome
                    )

                    print(
                        f"   Candidatos encontrados: "
                        f"{len(candidates)}"
                    )

                    # -----------------------------------------
                    # Nenhum candidato
                    # -----------------------------------------

                    if not candidates:

                        print(
                            "   ⚠️ Nenhum candidato."
                        )

                        continue

                    # -----------------------------------------
                    # RANKING
                    # -----------------------------------------

                    ranked = ordenar_resultados(
                        nome,
                        candidates
                    )

                    if not ranked:

                        print(
                            "   ⚠️ Nenhum resultado após "
                            "matching."
                        )

                        continue

                    # -----------------------------------------
                    # MELHOR RESULTADO
                    # -----------------------------------------

                    best = ranked[0]

                    score = best["score"]

                    print(
                        f"   🏆 Melhor candidato: "
                        f"{best['name']}"
                    )

                    print(
                        f"   📊 Score: {score}"
                    )

                    print(
                        f"   🔗 URL: {best['url']}"
                    )

                    # -----------------------------------------
                    # SCORE BAIXO
                    # -----------------------------------------

                    if score < 85:

                        print(
                            "   ❌ Score abaixo de 85."
                        )

                        continue

                    # -----------------------------------------
                    # REVISÃO MANUAL
                    # -----------------------------------------

                    if score < 95:

                        print(
                            "   ⚠️ Score entre 85 e 94.99."
                        )

                        print(
                            "   ⏭️ Pulando para evitar "
                            "preço incorreto."
                        )

                        continue

                    # -----------------------------------------
                    # MATCH AUTOMÁTICO
                    # -----------------------------------------

                    print(
                        "   ✅ MATCH AUTOMÁTICO"
                    )

                    # -----------------------------------------
                    # ABRIR PRODUTO
                    # -----------------------------------------

                    print(
                        "   🌐 Abrindo página do produto..."
                    )

                    product = site.get_product(
                        best["url"]
                    )

                    if not product:

                        print(
                            "   ❌ Não foi possível "
                            "obter os dados."
                        )

                        continue

                    # -----------------------------------------
                    # PREÇO
                    # -----------------------------------------

                    preco = product.get(
                        "price"
                    )

                    print(
                        f"   💰 Preço encontrado: "
                        f"{preco}"
                    )

                    if not preco:

                        print(
                            "   ⚠️ Produto encontrado, "
                            "mas preço não localizado."
                        )

                        continue

                    # -----------------------------------------
                    # SALVAR PREÇO
                    # -----------------------------------------

                    salvar_preco(
                        ws,
                        row,
                        preco
                    )

                    preco_encontrado = preco

                    print(
                        "   💾 Preço salvo na coluna E."
                    )

                    # -----------------------------------------
                    # NÃO PRECISA CONTINUAR NOS OUTROS SITES
                    # -----------------------------------------

                    break

                except Exception as e:

                    print(
                        f"   ❌ Erro no site "
                        f"{site_name}: {e}"
                    )

                    continue

            # -------------------------------------------------
            # RESULTADO DO PRODUTO
            # -------------------------------------------------

            if preco_encontrado:

                print()
                print(
                    f"✅ Produto finalizado: "
                    f"{preco_encontrado}"
                )

            else:

                print()
                print(
                    "⚠️ Nenhum preço automático "
                    "foi salvo."
                )

    finally:

        browser.close()

    # ---------------------------------------------------------
    # 6. GARANTIR DIRETÓRIO DE SAÍDA
    # ---------------------------------------------------------

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    # ---------------------------------------------------------
    # 7. SALVAR NOVA PLANILHA
    # ---------------------------------------------------------

    wb.save(
        OUTPUT_FILE
    )

    print()
    print("=" * 80)
    print("🎉 PROCESSAMENTO FINALIZADO")
    print("=" * 80)

    print()
    print(
        f"📁 Arquivo gerado:"
    )

    print(
        OUTPUT_FILE
    )

    print()
    print(
        "A planilha original não foi alterada."
    )


if __name__ == "__main__":
    main()