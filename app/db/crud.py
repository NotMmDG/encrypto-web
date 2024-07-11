from sqlalchemy.orm import Session
from app.db.models import User, File, UserCreate, FileCreate
from app.utils.security import get_password_hash

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    print(f"Creating user with email: {user.email}")
    print(f"Original password: {user.password}")
    print(f"Hashed password: {hashed_password}")
    
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Debug print to check if the user is created and committed correctly
    print(f"User created with ID: {db_user.id}, email: {db_user.email}")
    print(f"Stored hashed password: {db_user.hashed_password}")
    
    return db_user

def get_files_by_user(db: Session, user_id: int):
    return db.query(File).filter(File.owner_id == user_id).all()

def get_file_by_id(db: Session, file_id: int):
    return db.query(File).filter(File.id == file_id).first()

def create_file(db: Session, file: FileCreate):
    hashed_password = get_password_hash(file.password)
    db_file = File(
        filename=file.filename,
        file_content=file.file_content,
        hashed_password=hashed_password,
        owner_id=file.owner_id,
        password=file.password
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file