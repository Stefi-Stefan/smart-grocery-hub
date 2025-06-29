# app/routers/lists.py
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from app.models import GroceryItem, GroceryList
from app.database import engine

router = APIRouter(prefix="/lists", tags=["lists"])

@router.post("/", response_model=GroceryList)
def create_list(list_: GroceryList):
    with Session(engine) as session:
        session.add(list_)
        session.commit()
        session.refresh(list_)
        return list_

@router.post("/{list_id}/items", response_model=GroceryItem)
def add_item(list_id: int, item: GroceryItem):
    with Session(engine) as session:
        item.list_id = list_id
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

@router.get("/{list_id}/items", response_model=list[GroceryItem])
def get_items(list_id: int):
    with Session(engine) as session:
        statement = select(GroceryItem).where(GroceryItem.list_id == list_id)
        results = session.exec(statement).all()
        return results
