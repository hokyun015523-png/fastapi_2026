#===========================================================
# drug_storage/database.py
#===========================================================
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, DrugAgeContraindication

DB_URL = 'postgresql://postgres:1234@localhost:5432/kids_age_db'

engine = create_engine(DB_URL, echo=False)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("테이블 생성 완료")

def get_session():
    return SessionLocal()