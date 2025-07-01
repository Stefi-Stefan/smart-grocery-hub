from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)  # Email as the unique identifier
    hashed_password: str
    lists_owned: List["GroceryList"] = Relationship(back_populates="owner")
    lists_shared: List["GroceryList"] = Relationship(back_populates="shared_users")

class GroceryList(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    owner_email: str = Field(foreign_key="user.email")  # Use email for ownership
    owner: User = Relationship(back_populates="lists_owned")
    shared_users: List[User] = Relationship(back_populates="lists_shared")
