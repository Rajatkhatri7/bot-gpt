from pydantic import BaseModel,EmailStr

class LoginRequest(BaseModel):
    username: str
    password: str


class SignupRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str