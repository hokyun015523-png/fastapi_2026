'''
home_library_v1 / database.py
-----------------------------
예광탄 방식을 활용한 아주 얇은 코드
DB 연결 - postgreSQL
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# ── .env 파일 읽기 (NLK_CERT_KEY 등 비밀값을 코드에 직접 쓰지 않기 위함) ──
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = 'postgresql+psycopg2://postgres:1234@localhost:5432/home_library_v1'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

# FastAPI의 Depends(get_db)가 요청마다 이 함수를 호출해서 DB 세션을 하나씩 만들어준다.
# yield 이후의 db.close()는 요청 처리가 끝난 뒤 자동으로 실행되어 연결을 정리한다.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
