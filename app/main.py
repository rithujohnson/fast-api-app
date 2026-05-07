"""Fast API app entry point"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.seed import seed
from app.database.session import SessionLocal, engine
from app.database.base import Base
from app.routers.item_router import router as item_router
from app.routers.categories_router import router as categories_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(item_router)
app.include_router(categories_router)

@app.get("/")
def root() -> dict:
    return {"message": "Item API is running"}


@app.get("/health")
def health_check() -> dict:
    return {"status": "healthy"}
