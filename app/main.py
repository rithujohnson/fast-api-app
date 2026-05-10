"""Fast API app entry point"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.exceptions import InvalidCredentialsError, InsufficientPermissionsError
from app.schemas.error_schema import ErrorResponse
from app.database.seed import seed
from app.database.base import Base
from app.database.session import AsyncSessionLocal, engine
from app.routers.item_router import router as item_router
from app.routers.categories_router import router as categories_router
from app.routers.auth_router import router as auth_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        await seed(db)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(InvalidCredentialsError)
def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content=ErrorResponse(code=exc.code, message=str(exc)).model_dump(exclude_none=True),
    )


@app.exception_handler(InsufficientPermissionsError)
def insufficient_permissions_handler(request: Request, exc: InsufficientPermissionsError) -> JSONResponse:
    return JSONResponse(
        status_code=403,
        content=ErrorResponse(code=exc.code, message=str(exc)).model_dump(exclude_none=True),
    )

app.include_router(item_router)
app.include_router(categories_router)
app.include_router(auth_router)

@app.get("/")
def root() -> dict:
    return {"message": "Item API is running"}


@app.get("/health")
def health_check() -> dict:
    return {"status": "healthy"}
