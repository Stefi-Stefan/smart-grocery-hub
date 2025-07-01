from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from app.routers import lists, auth
from app.database import create_db_and_tables

app = FastAPI(title="Smart Grocery Hub")

# OAuth2 setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Include routers
app.include_router(auth.router)
app.include_router(lists.router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def root():
    return {"message": "Smart Grocery Hub API is running!"}
