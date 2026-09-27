import re
import unicodedata


def normalize_text(text):

    if not text:
        return ""

    text = str(text).lower()

    text = unicodedata.normalize(
        "NFKD",
        text
    )

    text = "".join(
        c for c in text
        if not unicodedata.combining(c)
    )

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def extract_price(text):

    if not text:
        return None

    matches = re.findall(
        r"R\$\s*[\d\.]+,\d{2}",
        text
    )

    if not matches:
        return None

    return matches[0]