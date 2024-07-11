from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_db
from app.db import crud
from app.db.models import User
from app.utils.security import verify_password, decrypt_file
from io import BytesIO

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

@router.get("/download", response_class=HTMLResponse)
def get_download(request: Request, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    files = crud.get_files_by_user(db, user_id=user.id)
    return templates.TemplateResponse("download.html", {"request": request, "user": user, "files": files})

@router.post("/download/{file_id}", response_class=HTMLResponse)
async def download_file(request: Request, file_id: int, password: str = Form(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_file = crud.get_file_by_id(db, file_id)
    if db_file is None or db_file.owner_id != user.id:
        raise HTTPException(status_code=404, detail="File not found or access denied")

    if not verify_password(password, db_file.password):
        print(password)
        print(db_file.password)
        return templates.TemplateResponse("download.html", {"request": request, "user": user, "files": crud.get_files_by_user(db, user_id=user.id), "error": "Invalid password"})

    decrypted_content = decrypt_file(db_file.file_content, password)
    file_like = BytesIO(decrypted_content)
    response = StreamingResponse(file_like, media_type="application/octet-stream")
    response.headers["Content-Disposition"] = f"attachment; filename={db_file.filename}"
    return response
