# ================================================
# storage_subway_busapi/02_bus/database.py
#
# PostgreSQL 연결 및 세션 관리
# (DB명: subwaydb, 비밀번호: 1234)
#
# 수집 과정에서 다 했는데 왜 다시 만드는가???
# --> 원본은 임시 적재였고, 
#       지금이 정식 저장모델 설계 단계
#
# ================================================
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DB_URL = 'postgresql://postgres:1234@localhost:5432/busapidb'
# echo=False --> 내부적으로 실행되는 SQL로그를 콘솔에 찍지 않는다(True로 바꾸면 디버깅에 유용)
engine = create_engine(DB_URL, echo=False) 

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    # Base를 상속받은 모든 모델(BusStop 등)의 테이블을 실제 DB에 생성
    # 이미 테이블이 존재하면 아무 동작도 하지 않는다.
    Base.metadata.create_all(bind=engine)
    print('[database] bus_stop 테이블 준비 완료 (정류소ID 기본키)')

def get_session():
    return SessionLocal()

if __name__ == '__main__':
    init_db()