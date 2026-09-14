from uuid import UUID

from pydantic import BaseModel, EmailStr


class FirmRegisterRequest(BaseModel):
    firm_name: str
    admin_email: EmailStr
    admin_password: str


class UserOut(BaseModel):
    id: UUID
    firm_id: UUID
    email: EmailStr
    role: str

    model_config = {"from_attributes": True}


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
