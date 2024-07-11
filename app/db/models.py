from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship, declarative_base
from pydantic import BaseModel, EmailStr

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))

    files = relationship("File", back_populates="owner")

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), index=True)
    file_content = Column(LargeBinary)
    hashed_password = Column(String(255))
    password = Column(String(255)) 
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="files")

# Pydantic schemas

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserSchema(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class FileBase(BaseModel):
    filename: str

class FileCreate(FileBase):
    file_content: bytes
    owner_id: int
    password: str

class FileSchema(FileBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
