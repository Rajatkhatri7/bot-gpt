
from jose import JWTError, jwt
from datetime import datetime, timedelta,time,timezone
from core.config import settings
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends,HTTPException,status
from db.session import get_db
from db.models.user import User
from sqlalchemy import select



oauth_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def create_token(data: dict, type: str,expires_minutes: int):
    try:

        to_encode = data.copy()
        
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
        jti = str(uuid.uuid4())
        to_encode.update({"exp": expire,"type":type,"jti":jti})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error encoding JWT")
    
    
async def get_decoded_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

async def verify_user(token: str = Depends(oauth_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = await get_decoded_token(token)
        if payload is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    email: str = payload.get("sub")
    user = await db.execute(select(User.email, User.password, User.id).filter(User.email == email))
    user = user.first()
    if user is None:
        raise credentials_exception
    return user
