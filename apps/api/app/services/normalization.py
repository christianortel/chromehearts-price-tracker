import re
import unicodedata
from hashlib import sha1


ABBREVIATIONS = {
    "ls": "long sleeve",
    "zipup": "zip up",
    "zip-up": "zip up",
    "zip hoodie": "zip up hoodie",
    "trucker cap": "trucker hat",
    "tee": "t shirt",
    "ch": "chrome hearts",
}

CATEGORY_KEYWORDS = {
    "trucker_hat": ["trucker", "hat", "cap"],
    "hoodie": ["hoodie", "pullover"],
    "zip_up": ["zip up", "zip", "zip hoodie"],
    "long_sleeve": ["long sleeve", "ls"],
    "ring": ["ring"],
    "bracelet": ["bracelet", "paper chain", "fancy"],
}

SIZE_PATTERN = re.compile(r"\b(xs|s|m|l|xl|xxl|small|medium|large|size\s+\d+|\d{1,2})\b", re.I)


def normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    for source, target in ABBREVIATIONS.items():
        text = re.sub(rf"\b{re.escape(source)}\b", target, text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def infer_category(normalized_title: str) -> str | None:
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in normalized_title for keyword in keywords):
            return category
    return None


def extract_size_token(value: str) -> str | None:
    match = SIZE_PATTERN.search(value)
    return match.group(1).lower() if match else None


def build_duplicate_group_key(source_name: str, normalized_title: str, price_amount: str, date_hint: str) -> str:
    payload = f"{source_name}|{normalized_title}|{price_amount}|{date_hint}"
    return sha1(payload.encode("utf-8")).hexdigest()

