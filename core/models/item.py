from pydantic import BaseModel, field_validator
from typing import Dict, Optional

class Item(BaseModel):
    # fixed fields:
    id: str                                # e.g. "white_bread"
    name: Dict[str, str]                   # e.g. {"en": "White Bread", "nl": "Wit brood", "fr": "Pain blanc", "de": "Weißbrot"}
    category_id: str                       # e.g. "grains"
    subcategory_id: Optional[str] = None   # e.g. "bread"
    icon: Optional[str] = None             # file/image path (later)
    # user variable fields:
    quantity: int = 1                      # quantity
    visible: bool = True                   # visibility
    note: Optional[str] = None             # user notes

    @field_validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('quantity can not be negative')
        return v