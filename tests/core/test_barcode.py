"""
Run all fast (mocked) tests:
    pytest -q tests/core/test_barcode.py

Run only real Open‑Food‑Facts API tests:
    pytest -m real_api -q tests/core/test_barcode.py

Run only local LibreTranslate tests:
    pytest -m local_translate -q tests/core/test_barcode.py
"""
import pytest
from unittest.mock import patch
from core.barcode import (
    lookup_barcode,
    translate_text_libre,
    translate_missing_languages,
)
from core.models.item import Item

# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------
SAMPLE_OFF_RESPONSE = {
    "status": 1,
    "product": {
        "product_name_en": "White Bread",
        "product_name_nl": "Wit brood",
        "product_name_fr": "Pain blanc",
        "product_name_de": "Weißbrot",
        "categories_tags": ["en:grains", "en:bread"],
    },
}

class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code

    def json(self):
        return self._json_data

    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception(f"HTTP {self.status_code}")

# ---------------------------------------------------------------------------
# Lookup‑barcode tests (mocked & real)
# ---------------------------------------------------------------------------
@patch("core.barcode.requests.get")
def test_lookup_barcode_success(mock_get):
    """OFF product found → correct Item created."""
    mock_get.return_value = MockResponse(SAMPLE_OFF_RESPONSE, 200)
    item = lookup_barcode("123456789")

    assert isinstance(item, Item)
    assert item.id == "white_bread"
    assert item.name["en"] == "White Bread"
    assert item.category_id == "grains"
    assert item.quantity == 1 and item.visible is True

@patch("core.barcode.requests.get")
def test_lookup_barcode_product_not_found(mock_get):
    mock_get.return_value = MockResponse({"status": 0}, 200)
    assert lookup_barcode("000000000") is None

@patch("core.barcode.requests.get")
def test_lookup_barcode_http_error(mock_get):
    mock_get.return_value = MockResponse({}, 500)
    assert lookup_barcode("error") is None

# --- Real OFF call (Nutella) -----------------------------------------------
@pytest.mark.real_api
def test_lookup_barcode_real_api_nutella():
    item = lookup_barcode("3017620422003")  # Nutella
    assert item and isinstance(item, Item)
    assert "nutella" in item.id.lower() or "nutella" in item.name.get("en", "").lower()

# --- Real OFF call that triggers our translation back‑fill ------------------
@pytest.mark.real_api
def test_lookup_barcode_translation_fill():
    """Uses a product that typically lacks Dutch/German names on OFF."""
    barcode = "5410126116953"  # Lotus Biscoff spread
    item = lookup_barcode(barcode)
    if item is None:
        pytest.skip("Barcode not found on OFF — skipping")

    names = item.name
    required = ["en", "nl", "fr", "de"]

    # All languages present & non‑empty
    for lang in required:
        assert lang in names and names[lang].strip()

# ---------------------------------------------------------------------------
# Translation unit tests (mocked requests.post)
# ---------------------------------------------------------------------------
@patch("core.barcode.requests.post")
def test_translate_text_libre_success(mock_post):
    mock_post.return_value = MockResponse({"translatedText": "Wit brood"}, 200)
    assert translate_text_libre("White Bread", "nl") == "Wit brood"

@patch("core.barcode.requests.post")
def test_translate_text_libre_failure(mock_post):
    mock_post.return_value = MockResponse({}, 500)
    assert translate_text_libre("White Bread", "nl") == "White Bread"

@patch("core.barcode.requests.post")
def test_translate_missing_all(mock_post):
    mock_post.side_effect = lambda url, json, timeout: MockResponse(
        {"translatedText": f"{json['q']} ({json['target']})"}, 200
    )
    names = translate_missing_languages({"en": "Bread"}, ["nl", "fr"])
    assert names["nl"].endswith("(nl)") and names["fr"].endswith("(fr)")

def test_translate_missing_no_en():
    names = {"nl": "Brood"}
    assert translate_missing_languages(names, ["fr"]) == names

# ---------------------------------------------------------------------------
# Local LibreTranslate integration test
# ---------------------------------------------------------------------------
@pytest.mark.local_translate
def test_local_libretranslate_roundtrip():
    """Hits the Docker container on localhost:5000."""
    text_en = "Hello world"
    text_fr = translate_text_libre(text_en, "fr")

    assert text_fr.lower() != text_en.lower()
    assert "bonjour" in text_fr.lower()
