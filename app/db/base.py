from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from env import settings

DATABASE_URL = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@db/{settings.MYSQL_DATABASE}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
