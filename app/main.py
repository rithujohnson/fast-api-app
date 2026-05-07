"""Fast API app entry point"""

from fastapi import FastAPI
from app.routers import item_router, categories_router


app = FastAPI(
    title="Item API",
    version="1.0.0",
    description="A learning project demonstrating a 3-layer FastAPI application.",
)

app.include_router(item_router.router)
app.include_router(categories_router.router)


@app.get("/")
def root() -> dict:
    return {"message": "Item API is running"}


@app.get("/health")
def health_check() -> dict:
    return {"status": "healthy"}
