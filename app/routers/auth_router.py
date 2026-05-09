from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.schemas.auth_schema import TokenResponse, UserRegisterRequest, UserResponse
from app.schemas.error_schema import ErrorResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _error(code: str, message: str) -> dict:
    return ErrorResponse(code=code, message=message).model_dump(exclude_none=True)


@router.post("/register", status_code=201, response_model=UserResponse)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)) -> UserResponse:
    try:
        user = auth_service.register_user(db, request)
        return UserResponse(id=user.id, username=user.username, role=user.role)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=_error(e.code, str(e)))


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    try:
        token = auth_service.login_user(db, form_data.username, form_data.password)
        return TokenResponse(access_token=token)
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=401, detail=_error(e.code, str(e)))