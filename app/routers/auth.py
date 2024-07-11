from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import timedelta

from app.db import crud
from app.db.base import SessionLocal
from app.utils.security import (
    verify_password, get_password_hash, create_access_token, verify_access_token
)
from app.db.models import UserCreate, UserSchema
from env import settings

router = APIRouter()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

templates = Jinja2Templates(directory="app/templates")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.get("/signup", response_class=HTMLResponse)
def get_signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/signup", response_class=HTMLResponse)
def post_signup(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=email)
    if db_user:
        return templates.TemplateResponse("signup.html", {"request": request, "error": "Email already registered"})
    
    print(f"Received signup request with email: {email} and password: {password}")
    
    user = UserCreate(email=email, password=password)
    created_user = crud.create_user(db=db, user=user)
    
    return templates.TemplateResponse("login.html", {"request": request, "msg": "User created successfully"})

@router.get("/login", response_class=HTMLResponse)
def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
def post_login(request: Request, db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...)):
    user = crud.get_user_by_email(db, email=username)
    if not user:
        print("User not found")
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect email or password"})
    
    print(f"Retrieved user: {user.email}")
    print(f"Stored hashed password: {user.hashed_password}")
    
    if not verify_password(password, user.hashed_password):
        print(f"Password verification failed for user: {user.email}")
        print(f"Input password: {password}")
        print(f"Stored hashed password: {user.hashed_password}")
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect email or password"})
    
    print("Password verification succeeded")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)
    
    print(f"Access token: {access_token}")
    
    response = templates.TemplateResponse("dashboard.html", {"request": request, "user": user})
    response.set_cookie(
        key="access_token", 
        value=f"Bearer {access_token}", 
        httponly=True,
        max_age=access_token_expires.total_seconds(), 
        expires=access_token_expires
    )
    
    return response

@router.get("/logout", response_class=RedirectResponse)
def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response
