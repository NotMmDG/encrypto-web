from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.dependencies import get_current_user, get_db
from sqlalchemy.orm import Session
from app.db.models import User
from app.db import crud

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    files = crud.get_files_by_user(db, user_id=user.id)
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "files": files})
