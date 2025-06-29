# app/models.py
from sqlmodel import SQLModel, Field
from typing import Optional

class GroceryItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    quantity: int = 1
    category: Optional[str] = None
    list_id: int

class GroceryList(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
