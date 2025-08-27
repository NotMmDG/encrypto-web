from fastapi import APIRouter, Depends, UploadFile, File, Form, Request, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from app.dependencies import get_current_user, get_db, get_current_user_id
from app.db import crud
from app.db.models import User, FileCreate, FileSchema
from app.utils.security import (
    get_password_hash,
    generate_password,
    encrypt_file,
    # NEW: wrapper that compresses with Huffman then encrypts
    encrypt_file_with_huffman,
)

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/upload", response_class=HTMLResponse)
def get_upload(request: Request, user: User = Depends(get_current_user)):
    return templates.TemplateResponse("upload.html", {"request": request, "user": user})

@router.post("/upload", response_class=JSONResponse)
async def post_upload(
    file: UploadFile = File(...),
    compression: str = Form("none"),  # "none" (default) or "huffman"
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Uploads a file and encrypts it. Optional compression step:
      - compression="none"   -> encrypt raw bytes
      - compression="huffman"-> Huffman-compress, then encrypt
      - compression="sha256" -> rejected (not a compression algorithm)
    """
    # Normalize/validate the compression choice
    compression = (compression or "none").strip().lower()
    if compression not in {"none", "huffman"}:
        if compression == "sha256":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="sha256 is a cryptographic hash, not a compression algorithm. Use 'none' or 'huffman'.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid compression. Allowed values: 'none', 'huffman'.",
        )

    # Read file bytes
    content = await file.read()

    # Generate per-file password and hash (you already persist the hash)
    password = generate_password()
    hashed_password = get_password_hash(password)

    # Compress (optional) then encrypt
    if compression == "huffman":
        encrypted_content = encrypt_file_with_huffman(content, password)
    else:
        encrypted_content = encrypt_file(content, password)

    new_file = FileCreate(
        filename=file.filename,
        file_content=encrypted_content,
        owner_id=current_user_id,
        password=hashed_password,
    )

    created_file = crud.create_file(db=db, file=new_file)

    return JSONResponse(
        content={
            "filename": created_file.filename,
            "id": created_file.id,
            "owner_id": created_file.owner_id,
            "password": password,        # Returning the password
            "compression": compression,  # Echo back what was applied
        }
    )
