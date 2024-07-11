from fastapi import APIRouter, Depends, UploadFile, File, Request, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from app.dependencies import get_current_user, get_db, get_current_user_id
from app.db import crud
from app.db.models import User, FileCreate, FileSchema
from app.utils.security import get_password_hash, generate_password, encrypt_file

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.get("/upload", response_class=HTMLResponse)
def get_upload(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("upload.html", {"request": request, "user": user})

@router.post("/upload", response_class=JSONResponse)
async def post_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    password = generate_password()
    hashed_password=get_password_hash(password)
    encrypted_content = encrypt_file(file.file.read(), password)
    new_file = FileCreate(
        filename=file.filename,
        file_content=encrypted_content,
        owner_id=current_user_id,
        password=hashed_password
    )
    
    created_file = crud.create_file(db=db, file=new_file)
    
    return JSONResponse(content={
        "filename": created_file.filename,
        "id": created_file.id,
        "owner_id": created_file.owner_id,
        "password": password  # Returning the password
    })