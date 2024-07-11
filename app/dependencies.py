from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.db import crud
from app.db.models import User
from app.db.base import SessionLocal
from env import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user_id(request: Request, db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = request.cookies.get("access_token")
    
    # Debugging information
    print(f"Access token from cookie: {token}")
    
    if not token:
        raise credentials_exception
    token = token.split(" ")[1] 
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError as e:
        print(f"JWT Error: {str(e)}")
        raise credentials_exception
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    return user_id

def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = get_current_user_id(request, db)
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
