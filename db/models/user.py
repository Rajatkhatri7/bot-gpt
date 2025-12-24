from sqlalchemy import Column,Integer,String,Boolean,Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
from db.base import Base




class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(100), unique=True, index=True)
    password = Column(String(100))

    

    