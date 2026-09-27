from rapidfuzz import fuzz
from utils import normalize_text


def score_nome(original, candidato):

    original = normalize_text(original)
    candidato = normalize_text(candidato)

    if not original or not candidato:
        return 0

    ratio = fuzz.ratio(
        original,
        candidato
    )

    token_sort = fuzz.token_sort_ratio(
        original,
        candidato
    )

    token_set = fuzz.token_set_ratio(
        original,
        candidato
    )

    wratio = fuzz.WRatio(
        original,
        candidato
    )

    score = (
        ratio * 0.20 +
        token_sort * 0.25 +
        token_set * 0.25 +
        wratio * 0.30
    )

    return round(score, 2)


def ordenar_resultados(nome, candidatos):

    resultados = []

    for candidato in candidatos:

        score = score_nome(
            nome,
            candidato["name"]
        )

        resultados.append({
            **candidato,
            "score": score
        })

    resultados.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return resultados