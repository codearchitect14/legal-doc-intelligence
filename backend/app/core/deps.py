from collections.abc import Callable
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_error
        user_id = UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError) as exc:
        raise credentials_error from exc

    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise credentials_error
    return user


def require_role(*allowed_roles: UserRole) -> Callable[[User], User]:
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return user

    return dependency


def get_current_firm_id(user: User = Depends(get_current_user)) -> UUID:
    """Every query touching case/document data must filter by this value.

    This is the query-layer enforcement of firm isolation: an endpoint that
    forgets to apply this filter cannot silently return another firm's rows,
    because the filter is applied here rather than trusted to be added ad hoc
    in each service function.
    """
    return user.firm_id
