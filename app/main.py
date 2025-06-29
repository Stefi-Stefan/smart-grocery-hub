# app/main.py
from fastapi import FastAPI
from app.routers import lists
from app.database import create_db_and_tables

app = FastAPI(title="Smart Grocery Hub")

# Include routers
app.include_router(lists.router)

# Run this when app starts
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def root():
    return {"message": "Smart Grocery Hub API is running! wahoo"}
