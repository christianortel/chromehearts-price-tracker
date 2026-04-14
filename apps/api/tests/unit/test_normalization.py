from app.services.normalization import (
    build_duplicate_group_key,
    extract_size_token,
    infer_category,
    normalize_text,
)


def test_normalize_text_expands_abbreviations_and_punctuation() -> None:
    assert normalize_text("CH LS Tee!!") == "chrome hearts long sleeve t shirt"


def test_infer_category_finds_ring_and_zip_up() -> None:
    assert infer_category("chrome hearts forever ring") == "ring"
    assert infer_category("chrome hearts cross patch zip up hoodie") == "zip_up"


def test_extract_size_token() -> None:
    assert extract_size_token("Chrome Hearts Hoodie Size XL") == "xl"


def test_duplicate_group_key_is_deterministic() -> None:
    first = build_duplicate_group_key("ebay", "chrome hearts forever ring", "495.00", "2026-04-01")
    second = build_duplicate_group_key("ebay", "chrome hearts forever ring", "495.00", "2026-04-01")
    assert first == second
