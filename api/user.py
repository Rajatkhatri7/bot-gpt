
from fastapi import APIRouter,Depends,HTTPException,Request,status
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.user import User
from db.session import get_db
from api.schemas.user import LoginRequest,SignupRequest
from core.config import settings
from passlib.hash import pbkdf2_sha256
from utils.auth_helper import create_token
from sqlalchemy import select


router = APIRouter()

@router.post("/signup")
async def signup(request: SignupRequest,db: AsyncSession = Depends(get_db)):
    email = request.email.strip()
    password = request.password.strip()

    user = await db.scalar(select(User).filter(User.email == email))
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    new_user = User(email=email, password=pbkdf2_sha256.hash(password))
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "User created successfully", "id": str(new_user.id), "email": new_user.email}

@router.post("/login")
async def login(request_data: LoginRequest,request:Request, db: AsyncSession = Depends(get_db)):
    username = request_data.username.strip()
    password = request_data.password.strip()

    user = await db.execute(select(User.email, User.password, User.id).filter(User.email == username))
    user = user.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not pbkdf2_sha256.verify(password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    access_token = await create_token(data={"sub": user.email},type="access",expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token = await create_token(data={"sub": user.email},type="refresh",expires_minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    return {"message": "Login successful", "access_token": access_token, "token_type": "bearer","expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES,"refresh_token": refresh_token,"refresh_token_expires_in": settings.REFRESH_TOKEN_EXPIRE_MINUTES}
