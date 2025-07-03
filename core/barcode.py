import requests
from typing import Optional, Dict
from core.models.item import Item
import re
import os

LT_URL = os.getenv("LIBRETRANSLATE_URL", "http://localhost:5000/translate")

def slugify(text: str) -> str:
    """Simple slugify: lowercase, replace spaces and non-alphanumeric with underscore."""
    return re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')

def translate_text_libre(text: str, target_lang: str) -> str:
    """
    Translate text using LibreTranslate (self‑hosted by default).
    """
    import requests

    try:
        resp = requests.post(
            LT_URL,
            json={
                "q": text,
                "source": "en",
                "target": target_lang.lower(),
                "format": "text",
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get("translatedText", text)
    except Exception:
        return text


def translate_missing_languages(names: Dict[str, str], target_langs: list[str]) -> Dict[str, str]:
    """
    Fills missing languages in 'names' dictionary by translating the English name.

    Args:
        names: Dictionary of language code -> name, e.g., {"en": "Apple"}.
        target_langs: List of language codes to fill if missing, e.g., ["nl", "fr", "de"].

    Returns:
        Updated 'names' dict with missing languages translated from English.
    """
    if "en" not in names or not names["en"]:
        # No English source to translate from
        return names

    for lang in target_langs:
        if lang not in names or not names[lang]:
            translated = translate_text_libre(names["en"], lang)
            names[lang] = translated
    return names

def lookup_barcode(barcode: str) -> Optional[Item]:
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") != 1:
            return None  # Product not found

        product = data["product"]

        # Extract English name or generic name for ID and names
        base_name = product.get("product_name_en") or product.get("product_name") or "unknown_product"
        item_id = slugify(base_name)

        # Extract available names
        names = {}
        for lang in ["en", "nl", "fr", "de"]:
            key = f"product_name_{lang}"
            if key in product and product[key]:
                names[lang] = product[key]

        # Fill missing languages
        names = translate_missing_languages(names, target_langs=["nl", "fr", "de"])

        # Category extraction - simple for now
        categories_tags = product.get("categories_tags", [])
        category_id = None
        if categories_tags:
            cat_tag = categories_tags[0]
            category_id = cat_tag.split(":")[1] if ":" in cat_tag else cat_tag
        else:
            category_id = "uncategorized"

        # No subcategory for now
        subcategory_id = None

        item = Item(
            id=item_id,
            name=names,
            category_id=category_id,
            subcategory_id=subcategory_id,
            icon=None,
            quantity=1,
            visible=True,
            note=None,
        )
        return item

    except Exception:
        return None
