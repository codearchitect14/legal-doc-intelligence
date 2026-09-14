from uuid import UUID

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.firm import Firm
from app.models.user import User, UserRole
from app.schemas.auth import (
    AccessToken,
    FirmRegisterRequest,
    RefreshRequest,
    TokenPair,
    UserOut,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register-firm", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_firm(payload: FirmRegisterRequest, db: Session = Depends(get_db)) -> User:
    existing = db.execute(
        select(User).where(User.email == payload.admin_email)
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    firm = Firm(name=payload.firm_name)
    db.add(firm)
    db.flush()

    admin_user = User(
        firm_id=firm.id,
        email=payload.admin_email,
        hashed_password=hash_password(payload.admin_password),
        role=UserRole.FIRM_ADMIN,
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    return admin_user


@router.post("/login", response_model=TokenPair)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> TokenPair:
    user = db.execute(select(User).where(User.email == form_data.username)).scalar_one_or_none()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenPair(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=AccessToken)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> AccessToken:
    invalid_token_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
    )
    try:
        decoded = decode_token(payload.refresh_token)
        if decoded.get("type") != "refresh":
            raise invalid_token_error
        user_id = UUID(decoded["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise invalid_token_error from exc

    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise invalid_token_error
    return AccessToken(access_token=create_access_token(user.id))
