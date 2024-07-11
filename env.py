import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MYSQL_USER: str = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD")
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE")
    MYSQL_ROOT_PASSWORD: str = os.getenv("MYSQL_ROOT_PASSWORD")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
settings = Settings()
